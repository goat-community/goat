import type { AppProps } from "next/app";
import { Provider } from "react-redux";

import store from "../store/index";
import "../styles/globals.css";
import "../styles/map.css";

export default function App({ Component, pageProps }: AppProps) {
  return (
    <Provider store={store}>
      <Component {...pageProps} />
    </Provider>
  );
}
