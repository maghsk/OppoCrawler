window.events = [];

function shimAll(){
	const funcs1 = {};
	const funcs2 = {};

	function shim(proto, name){
		const p = proto;
		if (!p[name]) return ;
		const f = p[name];

		funcs1[name] = f;
		function wrapped(){
			const err = new Error();
			window.events.push([performance.now(), name, err.stack, ...arguments]);
			const r = f.call(this, ...arguments);
			window.events.push([performance.now(), name + "End", err.stack, ...arguments]);
			return r;
		}
		p[name] = wrapped;
	}

	const proto = WebGLRenderingContext.prototype;
	const proto2 = WebGL2RenderingContext.prototype;

	for (const name in proto2){
		try { proto2[name];	} catch (e){ continue; }

		if (typeof proto2[name] === "function")
			shim(proto2, name);
	}
	// shim(proto2, "programBinary");
}