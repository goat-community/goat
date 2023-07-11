import Head from "next/head";
import React from "react";

import CustomMap from "../components/Map";

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
        <h1>Main Dashboard</h1>
        <CustomMap />
      </main>
    </>
  );
}
