import Head from "next/head";

export default function Home() {
  return (
    <>
      <Head>
        <title>Dashboard</title>
        <meta name="description" content="Data Dashboard" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <main>
        Main Dashboard
        {/* <Header />
                <SideMenu />
                <Dashboard /> */}
      </main>
    </>
  );
}
