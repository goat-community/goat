<template>
  <v-app id="inspire">
    <v-content>
      <v-container fluid fill-height class="pa-0">
        <v-layout justify-center>
          <v-row>
            <v-col cols="8" class="pa-0">
              <v-carousel
                height="100vh"
                interval="4000"
                cycle
                hide-delimiter-background
                hide-delimiters
                :show-arrows="false"
              >
                <v-carousel-item
                  v-for="(item, i) in carousels"
                  :key="i"
                  :src="item"
                ></v-carousel-item>
              </v-carousel>
            </v-col>

            <v-col class="elevation-5" cols="4">
              <div>
                <v-row
                  class="ma-0"
                  justify="center"
                  align="center"
                  style="padding-top:60px;padding-bottom:60px;padding-left:35px;padding-right:35px;min-width:300px;"
                >
                  <img src="img/goat_standard.svg" height="40px" />
                </v-row>
                <p class="mb-0 pb-0 ml-6">
                  {{ $t("login.title").toUpperCase() }}
                </p>
                <v-alert class="ma-2 mx-6" outlined v-if="errors" type="error">
                  {{ errors }}
                </v-alert>
                <v-card-text>
                  <v-form
                    ref="loginForm"
                    v-model="validLogin"
                    @keyup.native.enter="submitForm"
                    @submit.prevent="handleLogin"
                    class="mx-2"
                  >
                    <v-text-field
                      v-model="email"
                      outlined
                      name="email"
                      label="E-Mail"
                      type="text"
                      :rules="emailRules"
                      :disabled="loading"
                      validate-on-blur
                    ></v-text-field>
                    <v-text-field
                      v-model="password"
                      outlined
                      id="password"
                      name="password"
                      :label="$t('login.password')"
                      :append-icon="
                        password_visibility ? 'visibility' : 'visibility_off'
                      "
                      @click:append="
                        () => (password_visibility = !password_visibility)
                      "
                      :rules="passwordRules"
                      :type="password_visibility ? 'password' : 'text'"
                      :disabled="loading"
                      validate-on-blur
                    ></v-text-field>
                  </v-form>
                  <v-row class="mx-2 mt-n5 pt-0">
                    <v-spacer></v-spacer>
                    <a
                      style="z-index:2;color:#2BB381;text-decoration:none;"
                      href="https://plan4better.de/kontakt/"
                      >{{ $t("login.passwordForgotten") }}</a
                    >
                  </v-row>
                  <v-row class="mt-5 mx-0" align="center">
                    <v-col class="text-center">
                      <v-btn
                        height="50px"
                        width="100%"
                        class="text-xs-center white--text"
                        color="#2BB381"
                        :loading="loading"
                        @click="submitForm"
                      >
                        {{ $t("login.signIn") }}
                      </v-btn>
                    </v-col>
                  </v-row>
                  <v-row class="mx-3 mt-4 mb-0 pb-0">
                    <p class="font-weight-regular pb-0 mb-0">
                      {{ $t("login.noAccount") }}
                    </p>
                  </v-row>
                  <v-row class="mx-3">
                    <p class="font-weight-regular">
                      {{ $t("login.toSignUpContactUs") }}
                      <a
                        target="_blank"
                        style="color:#2BB381;text-decoration:none;"
                        href="https://plan4better.de/kontakt/"
                        class="text-body-1 link"
                        >Plan4better</a
                      >
                    </p>
                  </v-row>
                </v-card-text>
                <div style="position:absolute;bottom:20px;" class="mx-3">
                  <a href="https://plan4better.de/" target="_blank">
                    <img
                      style="cursor:pointer;"
                      src="img/plan4better_standard.svg"
                      height="30px"
                    />
                  </a>
                  <v-spacer></v-spacer>
                </div>
                <div style="position:absolute;bottom:20px;right:10px;">
                  <language></language>
                </div>
              </div>
            </v-col>
          </v-row>
        </v-layout>
      </v-container>
    </v-content>
  </v-app>
</template>

<script>
import { LOGIN } from "../store/actions.type";
import { mapState } from "vuex";
import Language from "../components/core/Language.vue";

export default {
  name: "Login",
  components: {
    language: Language
  },
  props: {
    source: String
  },
  data() {
    return {
      email: "",
      password: "",
      carousels: [
        "img/slider-images/image-1.png",
        "img/slider-images/image-2.png",
        "img/slider-images/image-3.png",
        "img/slider-images/image-4.png",
        "img/slider-images/image-5.png"
      ],
      password_visibility: String,
      rememberMe: true,
      validLogin: false,
      loading: false,
      passwordRules: [
        v => !!v || this.$t("login.passwordRequired"),
        v => v.length >= 4 || this.$t("login.maxFourChar")
      ],
      emailRules: [
        v => !!v || this.$t("login.mailRequired"),
        v =>
          /^(([^<>()[\]\\.,;:\s@']+(\.[^<>()\\[\]\\.,;:\s@']+)*)|('.+'))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/.test(
            v
          ) || this.$t("login.mailValid")
      ]
    };
  },
  methods: {
    submitForm() {
      this.$refs.loginForm.validate();
      this.$nextTick(() => {
        if (!this.validLogin) {
          this.loading = false;
          return;
        }
        this.loading = true;
        const formData = new FormData();
        formData.append("username", this.email.toLowerCase());
        formData.append("password", this.password);
        this.$store.dispatch(`auth/${LOGIN}`, formData).then(
          () => {
            this.loading = false;
            return this.$router.push({ name: "main" });
          },
          () => {
            this.loading = false;
          }
        );
      });
    }
  },
  computed: {
    ...mapState({
      errors: state => state.auth.errors
    })
  }
};
</script>

<style lang="scss" scoped>
.v-window {
  &-x-transition,
  &-x-reverse-transition,
  &-y-transition,
  &-y-reverse-transition {
    &-enter-active,
    &-leave-active {
      transition: 1.5s cubic-bezier(0.25, 0.8, 0.5, 1) !important;
    }
  }
}
</style>
