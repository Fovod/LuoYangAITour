export async function sendMessage(sessionId:string, content:string){
    const res = await fetch("http://127.0.0.1:8000/chat",{
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify({session_id:sessionId, user_input:content})
    })
    const data = await res.json();
    return data.reply;
}