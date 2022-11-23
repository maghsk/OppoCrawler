capturedWebGLFunctions = [];
let windowLoad = false;

console.log('inject.js loaded');

document.addEventListener('load', function() {
    console.log('windowLoad from inject.js');
    windowLoad = true;
}, false);


function injectCaptureShader() {
    const LIST_LIMIT = 2_000_000; //1_467_499 for aquarium
    let captureWebGL = true;

    // const funcs1 = {};
    // const funcs2 = {};

    // function shim(proto, name, funcs) {
    function shim(proto, name, gltype) {
        const f = proto[name];
        // funcs[name] = f;
        function wrapped() {
            if (captureWebGL) {
                const err = new Error();
                const start = performance.now();
                const r = f.call(this, ...arguments);
                const end = performance.now();
                capturedWebGLFunctions.push({
                    "gltype": gltype,
                    "start": start,
                    "time": end - start,
                    "funcName": name,
                    // "stack": err.stack,
                    "args": [...arguments]
                });
                if (capturedWebGLFunctions.length >= LIST_LIMIT || windowLoad) {
                    captureWebGL = false;
                }
                return r;
            } else {
                return f.call(this, ...arguments);
            }
        }
        proto[name] = wrapped;
    }

    const proto1 = WebGLRenderingContext.prototype;
    const proto2 = WebGL2RenderingContext.prototype;
    // shim(WebGLRenderingContext.prototype, "compileShader", funcs1);
    // shim(WebGL2RenderingContext.prototype, "compileShader", funcs2);
    // function shimAll(proto, funcs) {
    function shimAll(proto, gltype) {
        for (const name in proto){
            try { proto[name]; } catch (e){ continue; }
    
            if (typeof proto[name] === "function")
                // shim(proto, name, funcs);
                shim(proto, name, gltype);
        }
    }

    // shimAll(proto1, funcs1);
    shimAll(proto1, "WebGL 1");
    // shimAll(proto2, funcs2);
    shimAll(proto2, "WebGL 2");
}

function getCapturedWebGLFunctions() {
    // got some bugs here, large list will cause error
    return capturedWebGLFunctions;
}

function getJSONCapturedWebGLFunctions() {
    return JSON.stringify(capturedWebGLFunctions);
}

injectCaptureShader();

// TODO: extension implementation
// chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
//     console.log(sender.tab ?
//         "from a content script:" + sender.tab.url :
//         "from the extension");
//     return true;
//     if (request.action == "getShaders")
//         sendResponse(capturedWebGLFunctions);
// });