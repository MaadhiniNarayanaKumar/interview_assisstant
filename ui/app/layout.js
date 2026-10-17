import "./globals.css";

export const metadata = {
  title: "Interview Assistant",
  description: "Record or upload a self-introduction and review the feedback.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
