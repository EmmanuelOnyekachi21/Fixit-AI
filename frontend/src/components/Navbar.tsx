import { Menu, Shield, Zap } from 'lucide-react';

interface NavbarProps {
  onMenuClick: () => void;
}

export function Navbar({ onMenuClick }: NavbarProps) {
  return (
    <>
      <div className="sticky top-0 z-10 flex h-16 shrink-0 items-center gap-x-4 border-b border-gray-800 bg-gray-900 px-4 shadow-sm sm:gap-x-6 sm:px-6 lg:px-8">
        <button
          type="button"
          className="-m-2.5 p-2.5 text-gray-400 lg:hidden"
          onClick={onMenuClick}
        >
          <span className="sr-only">Open sidebar</span>
          <Menu className="h-6 w-6" aria-hidden="true" />
        </button>

        <div className="flex flex-1 gap-x-4 self-stretch lg:gap-x-6">
          <div className="flex items-center gap-x-3">
            <Shield className="h-8 w-8 text-blue-500" />
            <div>
              <h1 className="text-xl font-bold text-white">FixIt</h1>
              <p className="text-xs text-gray-400">Autonomous Security Agent</p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-x-4 lg:gap-x-6">
          <div className="hidden lg:block">
            <div className="flex items-center gap-2">
              <div className="h-2 w-2 rounded-full bg-green-500 animate-pulse"></div>
              <span className="text-sm text-gray-400">Powered by Gemini 3</span>
            </div>
          </div>
        </div>
      </div>
      
      {/* Demo Mode Banner */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 px-4 py-2 text-center">
        <div className="flex items-center justify-center gap-2 text-sm text-white">
          <Zap className="h-4 w-4" />
          <span className="font-semibold">LIVE DEMO MODE</span>
          <span className="hidden sm:inline">- Simulated data for hackathon presentation</span>
        </div>
      </div>
    </>
  );
}
