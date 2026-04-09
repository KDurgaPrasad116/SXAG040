import React, { useState, useEffect } from 'react';
import { Search, Bell, Moon, Sun, Mic, LogOut } from 'lucide-react';

const Header = () => {
  const [userInitial, setUserInitial] = useState('U');

  useEffect(() => {
    // Decode JWT to get email
    const token = localStorage.getItem('token');
    if (token) {
      try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        if (payload.sub) {
          setUserInitial(payload.sub[0].toUpperCase());
        }
      } catch (e) { /* ignore */ }
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('token');
    window.location.reload();
  };

  return (
    <header className="h-20 fixed top-0 right-0 left-64 glass z-40 flex items-center justify-between px-8">
      <div className="flex-1 max-w-2xl">
        <div className="relative group">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 group-focus-within:text-white transition-colors" size={20} />
          <input 
            type="text" 
            placeholder="Search documents, clauses, or ask the UI agent..." 
            className="w-full h-12 pl-12 pr-12 rounded-full glass-panel focus:outline-none focus:ring-1 focus:ring-white/30 transition-all font-medium text-white placeholder-slate-400"
          />
          <button className="absolute right-3 top-1/2 -translate-y-1/2 w-8 h-8 flex items-center justify-center rounded-full hover:bg-white/10 transition-colors text-slate-400 hover:text-white">
            <Mic size={18} />
          </button>
        </div>
      </div>
      
      <div className="flex items-center gap-4 ml-8">
        <button className="w-10 h-10 rounded-full glass-panel flex items-center justify-center hover:bg-white/10 transition-colors text-slate-300 relative">
          <Bell size={20} />
          <span className="absolute top-2 right-2 w-2 h-2 bg-red-500 rounded-full animate-pulse"></span>
        </button>
        
        <div className="h-10 w-10 rounded-full bg-gradient-to-tr from-legal-blue to-legal-teal ml-2 border-2 border-white dark:border-slate-800 shadow-md flex items-center justify-center text-white font-bold">
          {userInitial}
        </div>

        <button
          onClick={handleLogout}
          title="Logout"
          className="w-10 h-10 rounded-full glass-panel flex items-center justify-center hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors text-slate-500 hover:text-red-500 dark:hover:text-red-400"
        >
          <LogOut size={18} />
        </button>
      </div>
    </header>
  );
};

export default Header;
