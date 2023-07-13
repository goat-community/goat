import Head from "next/head";
import React from "react";

import Map from "../components/Map";

export default function Home() {
  return (
    <>
      <Head>
        <title>GOAT</title>
        <meta name="description" content="Data Dashboard" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <main>
        <h1>Map Demo</h1>

        <Map />
      </main>
    </>
  );
}
