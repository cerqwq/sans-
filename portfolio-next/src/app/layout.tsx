import type { Metadata } from "next";
import { Inter, JetBrains_Mono, Noto_Sans_SC } from "next/font/google";
import "./globals.css";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
  display: "swap",
});

const jetbrainsMono = JetBrains_Mono({
  variable: "--font-mono",
  subsets: ["latin"],
  display: "swap",
});

const notoSansSC = Noto_Sans_SC({
  variable: "--font-noto",
  subsets: ["latin"],
  weight: ["300", "400", "500", "700", "900"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "李宿 | 全栈开发工程师",
  description: "全栈开发工程师，专注于 Web 开发、UI 设计和游戏开发",
  keywords: ["全栈开发", "Web开发", "React", "Next.js", "游戏开发"],
  authors: [{ name: "李宿" }],
  openGraph: {
    title: "李宿 | 全栈开发工程师",
    description: "全栈开发工程师，专注于 Web 开发、UI 设计和游戏开发",
    type: "website",
    locale: "zh_CN",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="zh-CN"
      className={`${inter.variable} ${jetbrainsMono.variable} ${notoSansSC.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col bg-[#0c0b0a] text-[#f5f0e8]">
        {children}
      </body>
    </html>
  );
}
