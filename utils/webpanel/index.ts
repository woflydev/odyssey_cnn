import { serve } from "https://deno.land/std@0.184.0/http/server.ts";
const path = "/dev/shm/odyssey_tmp";
let activeSockets:WebSocket[] = [];
try{
    await Deno.stat(path)
}catch(_e){
    await Deno.mkdir(path)
}
function removeSocket(socket:WebSocket){
    activeSockets = activeSockets.filter(s => s !== socket);
    //@ts-ignore: GC?
    socket = null;
}

const handler = async (request: Request): Promise<Response> => {
    const { pathname } = new URL(request.url);

    if(request.headers.get("upgrade") === "websocket"){
        //!! upgrade to ws!
        const { socket, response } = Deno.upgradeWebSocket(request);
        
        socket.onmessage = e => {
            socket.send(Date.now() + " " + e.data);
        };
        socket.onerror = function () {
            removeSocket(socket)
            console.log("socket error");
        };
        socket.onclose = function () {
            removeSocket(socket)
            console.log("socket closed");
        };
        activeSockets.push(socket)
        return response;
    }
    if(pathname === "/frames"){
        const frames: string[] = [];
        for await(const {name, isFile} of Deno.readDir(path)){
            if(isFile && name.endsWith(".png")) frames.push(name.replace(".png", ""))
        }
        return new Response(JSON.stringify(frames), {
            headers:{
                "Content-Type": "application/json"
            }
        })
    }
    if(pathname.startsWith("/frame/")){
        return new Response(await Deno.readFile(`/dev/shm/odyssey_tmp/${pathname.replace("/frame/","")}.png`), {
            headers:{
                'Content-Type': 'image/png'
            }
        })
    }
    if(pathname === "/"){
        return new Response(await Deno.readFile('utils/webpanel/index.html'), {
            headers:{
                'Content-Type': 'text/html'
            }
        })
    }
    if(pathname === "/telementry"){
        return new Response(await Deno.readFile('/dev/shm/odyssey_tmp/telementry.txt'), {
            headers:{
                'Content-Type': 'text/plain'
            }
        })
    }

    return new Response("404 Not Found", {
        status: 404,
        headers: {
            "content-type": "text/plain",
        },
    });
};

serve(handler);

const watcher = Deno.watchFs(path);

(async function () {
    for await (const _ of watcher){
        const change = _.paths[0].replace(path,"").replace(".png", "").slice(1);
        for(const s of activeSockets){
            s.send(change)
        } 
    } 
})()