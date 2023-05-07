//@ts-check
const {createServer} = require("http");
const { createReadStream, watch} = require("fs");
const {readFile} = require("fs/promises")
const { readdir, mkdir, unlink } = require("fs/promises");
const WebSocketServer = require("ws/lib/websocket-server");
const path = "/dev/shm/odyssey_tmp/";

function getFramePath(frameName){
    return path + frameName + ".bmp";
}

/**
 * @type {Map<string, Buffer>}
 */
const cache = new Map();

async function cachedRead(frameName, forceUpdate = false){
    if(cache.has(frameName) && (!forceUpdate)){
        return cache.get(frameName)
    }else{
        try{
            let c = await readFile(getFramePath(frameName))
            cache.set(frameName, c);
            return c
        }catch(e){
            console.error(e)
            cache.delete(frameName);
            return false;
        }
    }
}
//clear path
const wss = new WebSocketServer({port: 8001})
let activeSockets = [];
(async function(){
    //set up directory if not exist, clear directory if it does
    try{
        for(let name of await readdir(path)){
            await unlink(path + name)
        }
        console.log("Clear folder successfully")
    }catch(e){
        await mkdir(path)
        console.log("Remade directory")
    }
    //websocket stuff
    wss.on("connection" , function(ws){
        activeSockets.push(ws);
        ws.on("error", console.error)
        ws.on('message', function message(data) {
            console.log('received: %s', data);
            ws.send(JSON.stringify({time: Date.now(), data}))
        });
        ws.on("close", function(){
            activeSockets = activeSockets.filter(s => s !== ws);
        })
    })
    /*watch(path, async function(change, name){
        const frameName = name.replace(".bmp", "");
        //update out own cache
        await cachedRead(frameName, true)//cache.set(frameName, await readFile(getFramePath(frameName)))
        console.log(Date.now() + ": notifying chages of "+ frameName)
        for(const s of activeSockets){
            s.send(JSON.stringify({change, frameName}))
        } 
    })*/

    // HTTP stuff
    function sendFile(res, path){
        createReadStream(path).pipe(res);
    }

    createServer(async (req, res) => {
        if(!req.url) req.url = ""
        if(req.url === "/frames"){
            res.statusCode = 200;
            res.end(JSON.stringify(
                (await readdir(path))
                    .filter(a => a.endsWith(".bmp"))
                    .map(a => a.replace(".bmp", ""))
            ))
            return;
        }else if(req.url.startsWith("/frame/")){
            let frameName = req.url.replace("/frame/","").replace(/\?.*$/, "");
            let d = await cachedRead(frameName);
            if(d){
                return res.end(d);
            }else{
                res.statusCode = 404;
                return res.end("Not Found")
            }
        }else if(req.url.startsWith("/forceFrameUpdate/")){
            let frameName = req.url.replace("/forceFrameUpdate/","").replace(/\?.*$/, "");
            await cachedRead(frameName, true)
            res.statusCode = 200
            res.end("Frame updated.")
            console.log(Date.now() + ": notifying chages of "+ frameName)
            for(const s of activeSockets){
                s.send(frameName)
            }
        }else if(req.url === "/"){
            return sendFile(res, 'utils/webpanel/index.html')
        }else if(req.url === "/telementry"){
            return sendFile(res, "/dev/shm/odyssey_tmp/telementry.txt")
        }else{
            res.statusCode = 404;
            res.end("404 Not Found")
        }
    }).listen(8000);
})()

