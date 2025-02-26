import React from 'react'

const Login = () => {
  return (
    <div className="bg-zinc-950 h-screen flex justify-center items-center">
      <div className="flex justify-center items-center flex-col py-4 px-4 gap-3 border-[0.1px] border-slate-500 rounded">
        <h1 className="text-2xl text-white font-extrabold">LOGIN</h1>

        <input 
          type="text" 
          placeholder="Email" 
          className="p-2 rounded border-[0.1px] text-slate-200 border-slate-500 bg-zinc-950"
        />
        
        <input 
          type="password" 
          placeholder="Password" 
          className="p-2 rounded text-slate-200 border-[0.1px] border-slate-500 bg-zinc-950"
        />

        <a href="#" className="text-white text-left w-full text-sm hover:font-extrabold duration-200">
          Forgot Password?
        </a>

        <button className="bg-sky-400 w-full py-2 text-white rounded hover:scale-105 duration-300 hover:bg-sky-500">
          LOGIN
        </button>

        <p className="text-white text-sm">
          Create a new account <a className="hover:font-extrabold duration-200 text-sky-300" href="#">here</a>
        </p>
      </div>
    </div>
  );
};

export default Login;
