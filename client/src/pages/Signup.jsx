import React from 'react'

const Signup = () => {
  return (
    <div className="bg-zinc-950 h-screen flex justify-center items-center">
  <div className="flex justify-center items-center flex-col py-4 px-8 gap-3 border-[0.1px] border-slate-500 rounded">
    <h1 className="text-2xl text-white font-extrabold">SIGN UP</h1>

    <input
      type="text"
      placeholder="Full Name"
      className="p-2 rounded border-[0.1px] text-slate-200 border-slate-500 bg-zinc-950 w-full"
    />
    <input
      type="email"
      placeholder="Email"
      className="p-2 w-full rounded border-[0.1px] text-slate-200 border-slate-500 bg-zinc-950"
    />
    <input
      type="password"
      placeholder="Password"
      className="p-2 rounded text-slate-200 border-[0.1px] border-slate-500 bg-zinc-950 w-full"
    />
    <input
      type="password"
      placeholder="Confirm Password"
      className="p-2 rounded text-slate-200 w-full border-[0.1px] border-slate-500 bg-zinc-950"
    />
    <button className="bg-sky-400 w-full py-2 text-white rounded hover:scale-105 duration-300 hover:bg-sky-500">
      SIGN UP
    </button>
    <p className="text-white text-sm">
      Already have an account{" "}
      <a className="hover:font-bold duration-200 text-sky-300" href="">
        Login here
      </a>
    </p>
  </div>
</div>

  )
}

export default Signup