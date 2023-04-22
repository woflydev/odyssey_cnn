import { serve } from "https://deno.land/std@0.184.0/http/server.ts";
let activeSockets:WebSocket[] = [];

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

    if(pathname === "/frame"){
        return new Response(await Deno.readFile('/dev/shm/frame.png'), {
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
        return new Response(await Deno.readFile('/dev/shm/telementry.txt'), {
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

const watcher = Deno.watchFs("/dev/shm/frame.png");

(async function () {
    for await (const _ of watcher){
        for(const s of activeSockets){
            s.send("frame")
        } 
    } 
})()