import Head from "next/head";
import { Translator, LocaleSwitcher } from "translations";


export default function Home() {
  return (
    <>
      <Head>
        <title>Goat</title>
      </Head>
      <h1>
        <Translator text="hello" />
        <LocaleSwitcher />
      </h1>
    </>
  );
}
