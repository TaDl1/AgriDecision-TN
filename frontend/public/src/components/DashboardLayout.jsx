import React, { useState } from 'react';
import {
  LayoutDashboard,
  History,
  BarChart3,
  LogOut,
  Menu,
  X,
  MapPin,
  Droplets,
  CloudRain,
  Info, // Imported Info icon

  ChevronRight,
  User
} from 'lucide-react';

const DashboardLayout = ({ children, user, activeView, onNavigate, onLogout }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'history', label: 'History', icon: History },
    { id: 'analytics', label: 'Analytics', icon: BarChart3 },
    { id: 'profile', label: 'Profile', icon: User },
    { id: 'about', label: 'About Us', icon: Info }, // Added About Us item
  ];

  return (
    <div className="min-h-screen bg-slate-50 flex">
      {/* Mobile Sidebar Overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed lg:static inset-y-0 left-0 z-50 w-64 bg-white border-r border-slate-200 transform transition-transform duration-200 ease-in-out lg:transform-none flex flex-col ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'
          }`}
      >
        {/* Logo Area */}
        <div className="p-6 border-b border-slate-100">
          <div className="flex items-center gap-3">
            <div className="text-3xl">🌾</div>
            <div>
              <h1 className="font-bold text-lg text-emerald-900 leading-tight">AgriDecision</h1>
              <p className="text-xs text-emerald-600 font-medium">Tunisia Edition</p>
            </div>
          </div>
        </div>

        {/* User Profile Summary */}
        <div className="p-4 mx-4 mt-6 bg-emerald-50 rounded-xl border border-emerald-100">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 rounded-full bg-emerald-100 flex items-center justify-center text-lg shadow-sm">
              👨‍🌾
            </div>
            <div className="min-w-0">
              <p className="font-semibold text-slate-900 text-sm truncate">
                {user.first_name && user.last_name
                  ? `${user.first_name} ${user.last_name}`
                  : (user?.phone ? `Farmer ${user.phone.slice(-4)}` : 'Welcome back')}
              </p>
              <p className="text-xs text-slate-500 truncate">
                {user.first_name ? '+216 ' + (user?.phone || '...') : ''}
              </p>
            </div>
          </div>
          <div className="space-y-2 text-xs">
            <div className="flex items-center gap-2 text-slate-600 bg-white/60 p-1.5 rounded-lg">
              <MapPin size={14} className="text-emerald-500" />
              <span className="font-medium">{user?.governorate || 'Tunis'}</span>
            </div>
            <div className="flex items-center gap-2 text-slate-600 bg-white/60 p-1.5 rounded-lg">
              {user?.farm_type === 'irrigated' ? (
                <Droplets size={14} className="text-blue-500" />
              ) : (
                <CloudRain size={14} className="text-sky-500" />
              )}
              <span className="font-medium">
                {user?.farm_type === 'irrigated' ? 'Irrigated Farm' : 'Rain-fed Farm'}
              </span>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-4 mt-8 space-y-1">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeView === item.id;

            return (
              <button
                key={item.id}
                onClick={() => {
                  onNavigate(item.id);
                  setSidebarOpen(false);
                }}
                className={`w-full flex items-center justify-between px-4 py-3 rounded-xl text-sm font-medium transition-all ${isActive
                  ? 'bg-emerald-600 text-white shadow-lg shadow-emerald-200'
                  : 'text-slate-600 hover:bg-slate-50 hover:text-emerald-700'
                  }`}
              >
                <div className="flex items-center gap-3">
                  <Icon size={20} className={isActive ? 'text-white' : 'text-slate-400'} />
                  <span>{item.label}</span>
                </div>
                {isActive && <ChevronRight size={16} className="opacity-75" />}
              </button>
            );
          })}
        </nav>

        {/* Logout */}
        <div className="p-4 border-t border-slate-100">
          <button
            onClick={onLogout}
            className="w-full flex items-center gap-3 px-4 py-3 text-sm font-medium text-slate-600 hover:text-red-600 hover:bg-red-50 rounded-xl transition-colors"
          >
            <LogOut size={20} />
            <span>Sign Out</span>
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col min-w-0 overflow-hidden relative">
        {/* Subtle Background Overlay */}
        <div
          className="absolute inset-0 z-0 pointer-events-none opacity-[0.03]"
          style={{
            backgroundImage: 'url(/wheat-bg.png)',
            backgroundSize: 'cover',
            backgroundPosition: 'center',
            backgroundAttachment: 'fixed'
          }}
        />

        {/* Mobile Header */}
        <header className="lg:hidden bg-white border-b border-slate-200 p-4 flex items-center justify-between sticky top-0 z-30">
          <div className="flex items-center gap-2">
            <div className="text-2xl">🌾</div>
            <span className="font-bold text-slate-900">AgriDecision</span>
          </div>
          <button
            onClick={() => setSidebarOpen(true)}
            className="p-2 text-slate-600 hover:bg-slate-100 rounded-lg transition-colors"
          >
            <Menu size={24} />
          </button>
        </header>

        {/* Scrollable Area */}
        <div className="flex-1 overflow-auto p-4 lg:p-10">
          <div className="w-full">
            {children}
          </div>

          {/* Footer */}
          <footer className="mt-12 border-t border-slate-200 pt-8 pb-4">
            <div className="w-full mx-auto text-center space-y-4">
              <div className="flex flex-col md:flex-row items-center justify-center gap-6 text-slate-600">
                <div className="flex items-center gap-2">
                  <span className="bg-emerald-100 p-2 rounded-full text-emerald-600">📧</span>
                  <div className="text-left">
                    <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Email Support</p>
                    <a href="mailto:support@agridecision.tn" className="font-semibold hover:text-emerald-600 transition-colors">
                      support@agridecision.tn
                    </a>
                  </div>
                </div>
                <div className="hidden md:block w-px h-10 bg-slate-200"></div>
                <div className="flex items-center gap-2">
                  <span className="bg-blue-100 p-2 rounded-full text-blue-600">📞</span>
                  <div className="text-left">
                    <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Call Us</p>
                    <a href="tel:+21671123456" className="font-semibold hover:text-blue-600 transition-colors">
                      +216 71 123 456
                    </a>
                  </div>
                </div>
              </div>

              <div className="text-sm text-slate-500 max-w-2xl mx-auto pt-4">
                <p className="italic">"Empowering Tunisian farmers with data-driven decisions for a sustainable future."</p>
                <p className="mt-2 text-xs">
                  &copy; {new Date().getFullYear()} AgriDecision Tunisia. All rights reserved.
                </p>
              </div>
            </div>
          </footer>
        </div>
      </main>
    </div>
  );
};

export default DashboardLayout;
