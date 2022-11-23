window.capturedWebGLFunctions = []

function injectCaptureShader() {
    // const funcs1 = {};
    // const funcs2 = {};

    // function shim(proto, name, funcs) {
    function shim(proto, name) {
        const f = proto[name];
        // funcs[name] = f;
        function wrapped() {
            const err = new Error();
            const start = performance.now();
            const r = f.call(this, ...arguments);
            const end = performance.now();
            window.capturedWebGLFunctions.push({
                "start": start,
                "time": end - start,
                "funcName": name,
                "stack": err.stack,
                "args": [...arguments]
            });
            return r;
        }
        proto[name] = wrapped;
    }

    const proto1 = WebGLRenderingContext.prototype;
    const proto2 = WebGL2RenderingContext.prototype;
    // shim(WebGLRenderingContext.prototype, "compileShader", funcs1);
    // shim(WebGL2RenderingContext.prototype, "compileShader", funcs2);
    // function shimAll(proto, funcs) {
    function shimAll(proto) {
        for (const name in proto){
            try { proto[name]; } catch (e){ continue; }
    
            if (typeof proto[name] === "function")
                // shim(proto, name, funcs);
                shim(proto, name);
        }
    }

    // shimAll(proto1, funcs1);
    shimAll(proto1);
    // shimAll(proto2, funcs2);
    shimAll(proto2);
}

injectCaptureShader();

// chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
//     console.log(sender.tab ?
//         "from a content script:" + sender.tab.url :
//         "from the extension");
//     return true;
//     if (request.action == "getShaders")
//         sendResponse(window.capturedWebGLFunctions);
// });