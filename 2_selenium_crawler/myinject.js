window.compiledShaders = []

function injectCaptureShader() {
    const funcs1 = {};
    const funcs2 = {};

    function shim(proto, name, funcs) {
        const f = proto[name];

        funcs[name] = f;
        function wrapped() {
            const err = new Error();
            const start = performance.now();
            const r = f.call(this, ...arguments);
            const end = performance.now();
            window.compiledShaders.push({
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

    // shim(WebGLRenderingContext.prototype, "compileShader", funcs1);
    // shim(WebGL2RenderingContext.prototype, "compileShader", funcs2);

    shim(WebGLRenderingContext.prototype, "shaderSource", funcs1);
    shim(WebGL2RenderingContext.prototype, "shaderSource", funcs2);
}

injectCaptureShader();

// chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
//     console.log(sender.tab ?
//         "from a content script:" + sender.tab.url :
//         "from the extension");
//     return true;
//     if (request.action == "getShaders")
//         sendResponse(window.compiledShaders);
// });