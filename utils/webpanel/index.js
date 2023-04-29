//@ts-check
const {createServer} = require("http");
const { createReadStream, watch} = require("fs");
const ws = require("ws");
const { readdir, mkdir, unlink } = require("fs/promises");
const WebSocketServer = require("ws/lib/websocket-server");
const path = "/dev/shm/odyssey_tmp";
//clear path
const wss = new WebSocketServer({port: 8001})
let activeSockets = [];
(async function(){
    //set up directory if not exist, clear directory if it does
    try{
        for(let name of await readdir(path)){
            await unlink(path +  "/" + name)
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
    watch(path, function(change, name){
        const file = name.replace(".png", "");
        for(const s of activeSockets){
            s.send({change, file})
        } 
    })

    // HTTP stuff
    function sendFile(res, path){
        createReadStream(path).pipe(res);
    }

    createServer(async (req, res) => {
        if(req.url === "/frames"){
            res.statusCode = 200;
            res.end(JSON.stringify(
                (await readdir(path))
                    .filter(a => a.endsWith(".png"))
                    .map(a => a.replace(".png", ""))
            ))
            return;
        }
        if(!req.url) req.url = ""
        if(req.url.startsWith("/frame/")){
            return sendFile(res, `/dev/shm/odyssey_tmp/${req.url.replace("/frame/","")}`)
        }
        if(req.url === "/"){
            return sendFile(res, 'utils/webpanel/index.html')
        }
        if(req.url === "/telementry"){
            return sendFile(res, "/dev/shm/odyssey_tmp/telementry.txt")
        }
        res.statusCode = 404;
        res.end("404 Not Found")
    }).listen(8000);

})()

