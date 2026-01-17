import React from 'react';
import {
    ArrowLeft,
    Sprout,
    RefreshCw,
    Users,
    Heart,
    Phone,
    MapPin,
    Calendar,
    Shield,
    BookOpen,
    Flag,
    Smartphone,
    Sun,
    Handshake,
    Brain,
    Mail,
    HelpCircle,
    ChevronRight,
    Search,
    CheckCircle
} from 'lucide-react';

const AboutScreen = ({ onBack }) => {
    // Forcing English as per user request
    const dir = 'ltr';

    return (
        <div className="w-full max-w-[1600px] mx-auto p-4 sm:p-10 space-y-20 pb-24 animate-fade-in text-slate-900" dir={dir}>
            {/* Navigation */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                    <button
                        onClick={onBack}
                        className="p-3 hover:bg-white hover:shadow-md rounded-2xl transition-all border border-transparent hover:border-slate-100"
                    >
                        <ArrowLeft className="text-slate-600" size={24} />
                    </button>
                    <div>
                        <h1 className="text-3xl font-black tracking-tight">About Us</h1>
                        <p className="text-slate-500 font-medium">Discover the AgriDecision story</p>
                    </div>
                </div>
            </div>

            {/* 1. HERO BANNER - Premium Implementation */}
            <div className="relative rounded-[3rem] overflow-hidden shadow-2xl min-h-[500px] flex items-center">
                {/* Background Image with Overlay */}
                <div className="absolute inset-0 z-0">
                    <img
                        src="/images/about/hero_premium.png"
                        alt="AgriDecision Hero"
                        className="w-full h-full object-cover"
                    />
                    <div className="absolute inset-0 bg-gradient-to-r from-emerald-950/90 via-emerald-900/60 to-transparent" />
                </div>

                <div className="relative z-10 p-8 sm:p-16 max-w-2xl space-y-8">
                    <div className="inline-flex items-center gap-2 px-4 py-2 bg-emerald-400/20 backdrop-blur-md rounded-full border border-emerald-400/30">
                        <Smartphone size={16} className="text-emerald-300" />
                        <span className="text-xs font-black uppercase tracking-widest text-emerald-100">Smart Technology</span>
                    </div>

                    <h2 className="text-4xl sm:text-6xl font-black text-white leading-[1.1] tracking-tight">
                        Smart Farming Advice <br />
                        <span className="text-emerald-400">for Tunisia.</span>
                    </h2>

                    <p className="text-emerald-50/80 text-xl font-medium leading-relaxed">
                        Combining traditional wisdom with modern technology to secure the future of our fields.
                    </p>

                    <div className="flex gap-4 pt-4">
                        <button onClick={onBack} className="bg-emerald-500 hover:bg-emerald-400 text-white font-black py-4 px-8 rounded-2xl shadow-lg transition-all hover:scale-105 active:scale-95 flex items-center gap-3">
                            Get Your Advice <ChevronRight size={20} />
                        </button>
                    </div>
                </div>
            </div>

            {/* 2. OUR MISSION - Integrated Content */}
            <section className="grid md:grid-cols-2 gap-12 items-center">
                <div className="space-y-8 order-2 md:order-1">
                    <div className="space-y-4">
                        <div className="bg-emerald-100 w-14 h-14 rounded-2xl flex items-center justify-center text-emerald-600 shadow-sm">
                            <Sprout size={32} />
                        </div>
                        <h3 className="text-4xl font-black tracking-tight">Why We Exist</h3>
                        <p className="text-slate-600 text-lg font-medium leading-relaxed">
                            Our mission is rooted in the deep soil of Tunisia, aiming to bridge the gap between ancestral knowledge and current environmental challenges.
                        </p>
                    </div>

                    <div className="grid gap-4">
                        {[
                            "To help Tunisian farmers make better planting decisions",
                            "Preserve generations of agricultural wisdom",
                            "Reduce crop losses due to weather uncertainty",
                            "Make farming knowledge accessible to everyone"
                        ].map((m, idx) => (
                            <div key={idx} className="flex gap-4 items-center p-4 bg-white rounded-2xl border border-slate-100 shadow-sm transition-all hover:shadow-md">
                                <CheckCircle className="text-emerald-500 shrink-0" size={24} />
                                <span className="font-bold text-slate-800">{m}</span>
                            </div>
                        ))}
                    </div>
                </div>
                <div className="relative order-1 md:order-2">
                    <div className="aspect-[4/5] rounded-[2.5rem] overflow-hidden shadow-2xl">
                        <img src="/images/about/mission_premium.png" alt="Our Mission" className="w-full h-full object-cover" />
                    </div>
                    {/* Decorative element */}
                    <div className="absolute -bottom-6 -right-6 w-32 h-32 bg-emerald-500/10 rounded-full blur-3xl" />
                </div>
            </section>

            {/* 3. HOW IT WORKS - Grid Based */}
            <section className="bg-slate-50 rounded-[3rem] p-8 sm:p-16 border border-slate-200">
                <div className="max-w-3xl mx-auto text-center space-y-4 mb-16">
                    <h3 className="text-4xl font-black tracking-tight">Traditional + Modern Science</h3>
                    <p className="text-slate-500 text-lg font-medium">We combine multiple data layers to provide the most accurate recommendations.</p>
                </div>

                <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
                    {[
                        { icon: Calendar, title: "Traditional Knowledge", desc: "8-season Tunisian agrarian calendar integrated.", color: "orange" },
                        { icon: Sun, title: "Modern Data", desc: "Real-time weather forecasts specific to your region.", color: "blue" },
                        { icon: Brain, title: "AI Analysis", desc: "Advanced risk assessment models for every crop.", color: "purple" },
                        { icon: Smartphone, title: "Simple Output", desc: 'Clear "Plant Now" or "Wait" recommendations.', color: "emerald", highlight: true }
                    ].map((item, idx) => (
                        <div key={idx} className={`p-8 rounded-[2rem] transition-all ${item.highlight ? 'bg-emerald-600 text-white shadow-xl scale-105 rotate-1' : 'bg-white border border-slate-200 text-slate-900 shadow-sm hover:shadow-xl'}`}>
                            <item.icon size={32} className={`mb-6 ${item.highlight ? 'text-white' : `text-${item.color}-600`}`} />
                            <h4 className="font-black text-xl mb-3">{item.title}</h4>
                            <p className={`font-medium leading-relaxed ${item.highlight ? 'text-emerald-50' : 'text-slate-500'}`}>{item.desc}</p>
                        </div>
                    ))}
                </div>
            </section>

            {/* 4. HERITAGE & LAND */}
            <div className="relative h-[400px] rounded-[3rem] overflow-hidden shadow-2xl group">
                <img src="/images/about/tradition_premium.png" alt="Tunisian Land" className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-1000" />
                <div className="absolute inset-0 bg-gradient-to-t from-slate-900/80 via-transparent to-transparent flex flex-col justify-end p-12">
                    <div className="flex items-center gap-3 mb-4">
                        <Flag className="text-red-500" size={24} />
                        <h3 className="text-3xl font-black text-white uppercase tracking-tight">Built for Our Land</h3>
                    </div>
                    <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
                        {[
                            "24 Governorates",
                            "Regional Differences",
                            "Local Crops",
                            "Rain-fed & Irrigated",
                            "Soil Type Precision"
                        ].map((txt, i) => (
                            <div key={i} className="px-6 py-4 bg-white/10 backdrop-blur-md rounded-2xl border border-white/20 text-white font-black text-center shadow-lg transform hover:scale-105 transition-transform cursor-default">
                                {txt}
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* 5. THE TEAM */}
            <section className="grid lg:grid-cols-5 gap-12 items-center">
                <div className="lg:col-span-3 aspect-video rounded-[2.5rem] overflow-hidden shadow-2xl relative">
                    <img src="/images/about/team_premium.png" alt="Our Team" className="w-full h-full object-cover" />
                    <div className="absolute inset-0 bg-gradient-to-r from-emerald-900/40 to-transparent" />
                </div>
                <div className="lg:col-span-2 space-y-8">
                    <div className="space-y-4">
                        <div className="bg-indigo-100 w-14 h-14 rounded-2xl flex items-center justify-center text-indigo-600">
                            <Users size={32} />
                        </div>
                        <h3 className="text-4xl font-black tracking-tight">Farmers & <br />Technologists</h3>
                        <p className="text-slate-600 font-medium leading-relaxed">
                            Created by experts in Tunis, guided by the wisdom of veteran farmers across the country.
                        </p>
                    </div>
                    <ul className="space-y-4">
                        {["Industry Experts", "Veteran Advisors", "Community Driven", "Continuously Improved"].map((item, i) => (
                            <li key={i} className="flex gap-4 items-center font-bold text-slate-800">
                                <div className="w-2 h-2 rounded-full bg-indigo-500" />
                                {item}
                            </li>
                        ))}
                    </ul>
                </div>
            </section>

            {/* 6. OUR VALUES */}
            <section className="text-center space-y-12">
                <div className="space-y-4">
                    <h3 className="text-4xl font-black tracking-tight">What We Believe In</h3>
                    <p className="text-slate-500 text-lg font-medium max-w-2xl mx-auto">Foundational principles that guide every feature we build.</p>
                </div>
                <div className="grid sm:grid-cols-3 gap-8">
                    {[
                        { icon: Heart, title: "Simplicity", desc: "No complex charts, just clear advice that works." },
                        { icon: Smartphone, title: "Accessibility", desc: "Optimized for speed on basic mobile networks." },
                        { icon: Shield, title: "Privacy", desc: "Your farm data is encrypted and remains yours." }
                    ].map((v, i) => (
                        <div key={i} className="p-10 bg-white rounded-[2.5rem] border border-slate-100 shadow-sm hover:shadow-2xl transition-all hover:-translate-y-2">
                            <v.icon size={48} className="text-emerald-500 mx-auto mb-6" />
                            <h4 className="text-2xl font-black mb-4">{v.title}</h4>
                            <p className="text-slate-600 font-medium leading-relaxed">{v.desc}</p>
                        </div>
                    ))}
                </div>
            </section>

            {/* 7. CONTACT & SUPPORT */}
            <section className="bg-[url('/images/about/almonds.png')] bg-cover bg-center rounded-[3.5rem] overflow-hidden shadow-2xl p-1">
                <div className="bg-emerald-950/90 p-8 sm:p-20 text-center backdrop-blur-sm rounded-[3.4rem] space-y-12 text-white">
                    <div className="space-y-4">
                        <h3 className="text-4xl sm:text-6xl font-black tracking-tight">We're Here to Help</h3>
                        <p className="text-emerald-100 text-xl font-medium opacity-80">Questions? Partnerships? Success stories?</p>
                    </div>

                    <div className="grid md:grid-cols-2 gap-6 max-w-3xl mx-auto">
                        <a href="mailto:support@agridecision.tn" className="flex items-center gap-6 bg-white/10 hover:bg-white p-6 rounded-3xl border border-white/20 transition-all group">
                            <Mail size={32} className="text-emerald-400 group-hover:text-emerald-600" />
                            <div className="text-left">
                                <p className="text-xs font-black text-emerald-300 uppercase tracking-widest mb-1">Support</p>
                                <span className="font-bold text-lg group-hover:text-slate-900">support@agridecision.tn</span>
                            </div>
                        </a>
                        <a href="mailto:hello@agridecision.tn" className="flex items-center gap-6 bg-white/10 hover:bg-white p-6 rounded-3xl border border-white/20 transition-all group">
                            <Handshake size={32} className="text-blue-400 group-hover:text-blue-600" />
                            <div className="text-left">
                                <p className="text-xs font-black text-blue-300 uppercase tracking-widest mb-1">Partnerships</p>
                                <span className="font-bold text-lg group-hover:text-slate-900">hello@agridecision.tn</span>
                            </div>
                        </a>
                    </div>

                    <div className="flex flex-wrap justify-center gap-8 pt-8 border-t border-white/10 text-emerald-200/60 font-black text-sm uppercase tracking-widest">
                        <span className="hover:text-white cursor-pointer transition-colors">Privacy Policy</span>
                        <span className="hover:text-white cursor-pointer transition-colors">Terms of Service</span>
                        <span className="hover:text-white cursor-pointer transition-colors">Help Center</span>
                    </div>
                </div>
            </section>

            {/* Final Message */}
            <footer className="text-center space-y-8 pt-12">
                <p className="italic text-slate-400 font-bold text-xl max-w-2xl mx-auto leading-relaxed">
                    "Together, we're building a smarter future for Tunisian agriculture—one planting decision at a time."
                </p>
                <div className="h-2 w-24 bg-emerald-500 mx-auto rounded-full" />
            </footer>
        </div>
    );
};

export default AboutScreen;
