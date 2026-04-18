/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { motion } from "motion/react";
import { 
  Bot, 
  Cpu, 
  Layers, 
  Zap, 
  BarChart3, 
  Terminal, 
  Layout, 
  MessageSquare,
  Circle
} from "lucide-react";

export default function App() {
  return (
    <div className="grid-main" dir="rtl">
      {/* Header */}
      <header className="col-span-full glass-panel border-b flex items-center justify-between px-6 z-50">
        <div className="flex items-center gap-3">
          <div className="w-3 h-3 bg-[var(--accent)] rounded-sm neon-shadow animate-pulse" />
          <h1 className="font-extrabold text-lg tracking-widest text-[var(--accent)] uppercase">
            EE-TUTOR PRO V1.1
          </h1>
        </div>
        <div className="font-mono text-[10px] text-[var(--text-secondary)] hidden md:block">
          [ SYSTEM STATUS: OPERATIONAL ] [ LATENCY: 12ms ] [ ENGINE: LLM7.IO ]
        </div>
        <div className="text-[10px] uppercase tracking-wider text-[var(--text-secondary)]">
          ENGINEER: AI SPECIALIST
        </div>
      </header>

      {/* Sidebar */}
      <aside className="glass-panel border-l p-5 flex flex-col gap-6 overflow-y-auto">
        <section>
          <h2 className="text-[10px] uppercase tracking-widest text-[var(--accent)] opacity-80 mb-3 flex items-center gap-2">
            <Cpu size={12} /> System Environment
          </h2>
          <div className="bg-black/30 border border-[var(--border)] p-3 rounded-lg">
            <TechItem label="Runtime" val="Python 3.12.10" />
            <TechItem label="Engine" val="PTB v21.x" />
            <TechItem label="Provider" val="LLM7.io" />
            <TechItem label="Vector DB" val="FAISS-CPU" />
          </div>
        </section>

        <section>
          <h2 className="text-[10px] uppercase tracking-widest text-[var(--accent)] opacity-80 mb-3 flex items-center gap-2">
            <Layers size={12} /> Project Structure
          </h2>
          <div className="font-mono text-[11px] text-[var(--text-secondary)] leading-relaxed space-y-1">
            <p className="hover:text-[var(--accent)] cursor-pointer">/src</p>
            <p className="pl-4 hover:text-[var(--accent)] cursor-pointer">├─ bot/ (Handlers)</p>
            <p className="pl-4 hover:text-[var(--accent)] cursor-pointer">├─ tutor/ (Logic)</p>
            <p className="pl-4 hover:text-[var(--accent)] cursor-pointer">├─ retrieval/ (RAG)</p>
            <p className="pl-4 hover:text-[var(--accent)] cursor-pointer">├─ quiz/ (Eval)</p>
            <p className="pl-4 hover:text-[var(--accent)] cursor-pointer">└─ main.py</p>
          </div>
        </section>

        <section className="mt-auto">
          <div className="p-3 bg-[var(--accent)]/10 border border-[var(--accent)]/20 rounded-lg text-center">
            <span className="text-[10px] uppercase font-bold text-[var(--accent)]">
              Bot Active
            </span>
          </div>
        </section>
      </aside>

      {/* Main Content */}
      <main className="p-6 flex flex-col gap-6 bg-black/10 overflow-hidden">
        {/* Schematic View */}
        <section className="flex-1 border border-dashed border-[var(--border)] rounded-2xl relative bg-[radial-gradient(circle_at_center,_rgba(15,23,42,1)_0%,_transparent_100%)]">
          <SchematicNode top="10%" left="50%" label="Telegram API" sub="Interaction Layer" active />
          <SchematicNode top="45%" left="20%" label="Vision Module" sub="Circuit Analysis" />
          <SchematicNode top="45%" right="20%" label="RAG Engine" sub="PDF Knowledge" delay={0.2} />
          <SchematicNode bottom="10%" left="50%" label="LLM7 Core" sub="Reasoning & Solver" active delay={0.4} />
          
          {/* Animated Connectors */}
          <div className="absolute top-[20%] left-[35%] w-[1px] h-[30%] bg-[var(--accent)]/30 -rotate-[60deg]" />
          <div className="absolute top-[20%] right-[35%] w-[1px] h-[30%] bg-[var(--accent)]/30 rotate-[60deg]" />
          <div className="absolute bottom-[20%] left-[35%] w-[1px] h-[30%] bg-[var(--accent)]/30 rotate-[60deg]" />
          <div className="absolute bottom-[20%] right-[35%] w-[1px] h-[30%] bg-[var(--accent)]/30 -rotate-[60deg]" />
        </section>

        {/* Bottom Details Row */}
        <div className="flex gap-6 h-[280px]">
          <div className="flex-1 glass-panel border rounded-2xl p-6 bg-black/40">
            <h2 className="text-[10px] uppercase tracking-widest text-[var(--accent)] mb-4 flex items-center gap-2">
              <Terminal size={12} /> Persian Logic Integration
            </h2>
            <p className="text-xs text-[var(--text-secondary)] mb-4 leading-relaxed">
              سیستم برای آموزش مفاهیم پیچیده برق به زبان فارسی بهینه شده است. با استفاده از پرامپت‌های مهندسی‌شده، ربات توانایی تحلیل گام‌به‌گام مسائل و مدارها را دارد.
            </p>
            <div className="border-r-4 border-[var(--accent)] bg-white/5 p-4 rounded-lg space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-[10px] uppercase opacity-50">Current Mode</span>
                <span className="text-[var(--accent)] font-bold text-xs">SOLVER</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-[10px] uppercase opacity-50">Topic</span>
                <span className="text-xs">Laplace Transforms</span>
              </div>
            </div>
          </div>

          {/* Telegram Mockup */}
          <div className="w-[320px] telegram-window">
            <div className="bg-[#17212b] p-3 border-b border-[#0e1621] flex items-center gap-3">
              <div className="w-8 h-8 rounded-full bg-[var(--accent)] flex items-center justify-center text-black">
                <Bot size={18} />
              </div>
              <div>
                <h3 className="text-sm font-bold text-white leading-none">EE Personal Tutor</h3>
                <span className="text-[10px] text-[var(--accent)]">bot is typing...</span>
              </div>
            </div>
            
            <div className="flex-1 p-4 space-y-3 overflow-y-auto">
              <motion.div initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} className="msg-bot">
                سلام! من دستیار هوشمند مهندسی برق شما هستم. چه کمکی از دستم برمی‌آید؟
              </motion.div>
              <motion.div initial={{ opacity: 0, x: 10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.5 }} className="msg-user">
                می‌تونی این مدار رو برام تحلیل کنی؟
              </motion.div>
              <motion.div initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 1 }} className="msg-bot">
                حتماً! لطفاً تصویر مدار یا پارامترهای قطعات را بفرستید.
              </motion.div>
            </div>

            <div className="bg-[#17212b] p-2 grid grid-cols-2 gap-1.5 border-t border-[#0e1621]">
              <TelegramBtn label="📚 انتخاب درس" />
              <TelegramBtn label="📝 کوییز جدید" />
              <TelegramBtn label="📊 پیشرفت من" />
              <TelegramBtn label="⚙️ تنظیمات" />
            </div>
          </div>
        </div>
      </main>

      {/* Footer Stats */}
      <footer className="col-span-full glass-panel border-t p-6 grid grid-cols-4 gap-6">
        <StatCard label="Active Users" val="1.2k" />
        <StatCard label="Files Indexed" val="452" />
        <StatCard label="Avg Inference" val="0.8s" />
        <StatCard label="Accuracy Rate" val="98.2%" />
      </footer>
    </div>
  );
}

function TechItem({ label, val }: { label: string; val: string }) {
  return (
    <div className="tech-item">
      <span>{label}</span>
      <span className="tech-val">{val}</span>
    </div>
  );
}

function SchematicNode({ top, left, right, label, sub, active, delay = 0 }: any) {
  return (
    <motion.div 
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ delay }}
      className="absolute glass-panel border-2 rounded-lg p-3 text-center w-[140px] z-10 neon-shadow"
      style={{ top, left: left || 'auto', right: right || 'auto', transform: left ? 'translateX(-50%)' : 'none', borderColor: active ? 'var(--accent)' : 'var(--border)' }}
    >
      <div className="text-[11px] font-bold tracking-tight">{label}</div>
      <div className="text-[8px] text-[var(--text-secondary)] uppercase">{sub}</div>
    </motion.div>
  );
}

function TelegramBtn({ label }: { label: string }) {
  return (
    <div className="bg-[#242f3d] py-2 text-center text-[10px] rounded border border-transparent hover:border-[#6ab3f3]/30 cursor-pointer text-[#6ab3f3] transition-colors">
      {label}
    </div>
  );
}

function StatCard({ label, val }: { label: string; val: string }) {
  return (
    <div className="flex flex-col gap-1">
      <span className="text-[10px] uppercase tracking-widest text-[var(--text-secondary)] font-medium">
        {label}
      </span>
      <motion.span 
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="text-3xl font-light font-mono text-[var(--accent)]"
      >
        {val}
      </motion.span>
    </div>
  );
}
