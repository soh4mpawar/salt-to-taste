"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Home, Beaker, Heart, Clock } from "lucide-react";

const navItems = [
  { href: "/", label: "Cook", icon: Home },
  { href: "/converter", label: "Convert", icon: Beaker },
  { href: "/health", label: "Health", icon: Heart },
  { href: "/history", label: "History", icon: Clock },
];

export function BottomNav() {
  const pathname = usePathname();
  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-white border-t border-salt-200 px-2 pb-[env(safe-area-inset-bottom)] z-40">
      <div className="flex max-w-[500px] mx-auto">
        {navItems.map(({ href, label, icon: Icon }) => {
          const active = pathname === href;
          return (
            <Link key={href} href={href}
              className={`flex-1 flex flex-col items-center justify-center gap-1 py-3 min-h-touch
                ${active ? "text-umami-500" : "text-salt-500 hover:text-salt-900 transition-colors"}`}
            >
              <Icon size={22} strokeWidth={active ? 2.5 : 1.5} />
              <span className="text-xs font-medium">{label}</span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
