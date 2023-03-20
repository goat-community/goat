<template>
  <div class="container">
    <h2>
      <img
        src="https://raw.githubusercontent.com/cinaaaa/reado/main/tools.webp"
        width="250"
        height="250"
        alt="tool"
      />
    </h2>
    <div class="content">
      <h1 class="main-heading">Under Maintenance!</h1>
      <p>
        Our services are currently under maintenance. We kindly ask you for your
        patience. Soon we will be online again.
      </p>
      <a href="https://plan4better.de/" target="blank">
        <button>Back to Plan4Better</button>
      </a>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import { mapFields } from "vuex-map-fields";
import { LOGOUT } from "../store/actions.type";
import router from "../router";
import store from "../store/index";
export default {
  computed: {
    ...mapFields("app", {
      healthZCancelToken: "healthZCancelToken"
    })
  },
  mounted() {
    document.title = "Plan4Better - Under Maintenance";

    const CancelToken = axios.CancelToken;
    const axiosInstance = axios.create();
    delete axiosInstance.defaults.headers.common["Authorization"];
    axiosInstance.defaults.baseURL = "./api";
    const intervalId = window.setInterval(function() {
      if (this.healthZCancelToken instanceof Function) {
        this.healthZCancelToken("cancelled");
        this.healthZCancelToken = null;
      }
      axiosInstance
        .get("/status", {
          responseType: "arraybuffer",
          cancelToken: new CancelToken(c => {
            // An executor function receives a cancel function as a parameter
            this.healthZCancelToken = c;
          })
        })
        .then(() => {
          window.clearInterval(intervalId);
          store.dispatch(`auth/${LOGOUT}`);
          router.push({ name: "login" });
        })
        .catch(e => {
          console.log(e);
        });
    }, 4000);
  }
};
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: "Poppins", sans-serif;
}

h2 {
  font-size: 10rem !important;
  font-weight: bold;
  color: #2bb381;
  display: flex;
  justify-content: center;
}

.container {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.content {
  text-align: center;
  margin: 3rem 0;
}

.content .main-heading {
  font-size: 2.5rem;
  font-weight: 700;
}

p {
  font-size: 1.3rem;
  padding: 0.7rem 0;
}

button {
  padding: 1rem;
  border-radius: 15px;
  outline: none;
  border: none;
  background: #2bb381;
  color: #fff;
  font-size: 1.3rem;
  cursor: pointer;
}
</style>
