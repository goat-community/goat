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

                <v-alert class="ma-2 mx-6" outlined v-if="errors" type="error">
                  {{ errors }}
                </v-alert>
                <v-alert
                  v-if="message"
                  outlined
                  class="ma-2 mx-6"
                  icon="fa-solid fa-circle-check"
                  color="#2BB381"
                >
                  {{ message }}
                </v-alert>
                <!-- Sign in   -->
                <v-card-text v-if="$route.name === 'login'">
                  <h3 class="mb-0 pb-0 ml-2 mb-4 font-weight-regular">
                    {{ $t("login.title").toUpperCase() }}
                  </h3>
                  <v-form
                    ref="authForm"
                    v-model="validForm"
                    @keyup.native.enter="submitLoginForm"
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
                        password_visibility ? 'visibility_off' : 'visibility'
                      "
                      @click:append="
                        () => (password_visibility = !password_visibility)
                      "
                      :rules="passwordRules"
                      :type="password_visibility ? 'text' : 'password'"
                      :disabled="loading"
                      validate-on-blur
                    ></v-text-field>
                  </v-form>
                  <v-row class="mx-2 mt-n5 pt-0">
                    <v-spacer></v-spacer>
                    <router-link
                      style="z-index:2;color:#2BB381;text-decoration:none;"
                      to="/forgot-password"
                      >{{ $t("login.passwordForgotten") }}</router-link
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
                        @click="submitLoginForm"
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

                <!-- Forgot password  -->
                <v-card-text v-if="$route.name === 'forgot-password'">
                  <h3 class="mb-0 pb-0 ml-2 mb-2 font-weight-regular">
                    {{ $t("login.forgotYourPassword").toUpperCase() }}
                  </h3>
                  <p class="mb-0 pb-0 ml-2 mb-4 body-2">
                    {{ $t("login.forgotPasswordText") }}
                  </p>
                  <v-form
                    ref="authForm"
                    v-model="validForm"
                    @keyup.native.enter="submitForgotPasswordForm"
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
                  </v-form>
                  <v-row class="mx-2 mt-n5 pt-0">
                    <v-spacer></v-spacer>
                    <router-link
                      style="z-index:2;color:#2BB381;text-decoration:none;"
                      to="/login"
                      >{{ $t("login.backToLogin") }}</router-link
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
                        @click="submitForgotPasswordForm"
                      >
                        {{ $t("login.sendResetLink") }}
                      </v-btn>
                    </v-col>
                  </v-row>
                </v-card-text>

                <!-- Reset password -->
                <v-card-text v-if="$route.name === 'reset-password'">
                  <h3 class="mb-0 pb-0 ml-2 mb-4 font-weight-regular">
                    {{ $t("login.resetYourPassword").toUpperCase() }}
                  </h3>

                  <v-form
                    ref="authForm"
                    v-model="validForm"
                    @keyup.native.enter="submitResetPasswordForm"
                    class="mx-2"
                  >
                    <v-text-field
                      v-model="password"
                      outlined
                      id="password"
                      name="password"
                      :label="$t('login.newPassword')"
                      :append-icon="
                        password_visibility ? 'visibility_off' : 'visibility'
                      "
                      @click:append="
                        () => (password_visibility = !password_visibility)
                      "
                      :rules="passwordRules"
                      :type="password_visibility ? 'text' : 'password'"
                      :disabled="loading"
                      validate-on-blur
                    ></v-text-field>
                    <v-text-field
                      v-model="confirmPassword"
                      outlined
                      :rules="[passwordMatch]"
                      :append-icon="
                        confirmPassword_visibility
                          ? 'visibility_off'
                          : 'visibility'
                      "
                      :type="confirmPassword_visibility ? 'text' : 'password'"
                      :label="$t('login.confirmPassword')"
                      @click:append="
                        confirmPassword_visibility = !confirmPassword_visibility
                      "
                    ></v-text-field>
                  </v-form>
                  <v-row class="mx-2 mt-n5 pt-0">
                    <v-spacer></v-spacer>
                    <router-link
                      style="z-index:2;color:#2BB381;text-decoration:none;"
                      to="/login"
                      >{{ $t("login.backToLogin") }}</router-link
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
                        @click="submitResetPasswordForm"
                      >
                        {{ $t("login.resetPassword") }}
                      </v-btn>
                    </v-col>
                  </v-row>
                </v-card-text>

                <!-- Bottom -->
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
import { LOGIN, FORGOT_PASSWORD, RESET_PASSWORD } from "../store/actions.type";
import { mapState, mapMutations } from "vuex";
import Language from "../components/core/Language.vue";
import { SET_ERROR, SET_MESSAGE } from "../store/mutations.type";
import jwt_decode from "jwt-decode";

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
      token: "",
      email: "",
      password: "",
      confirmPassword: "",
      carousels: [
        "img/slider-images/image-1.png",
        "img/slider-images/image-2.png",
        "img/slider-images/image-3.png",
        "img/slider-images/image-4.png",
        "img/slider-images/image-5.png"
      ],
      password_visibility: false,
      confirmPassword_visibility: false,
      rememberMe: true,
      // Form validation
      validForm: false,
      // Rules
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
      ],
      loading: false
    };
  },
  methods: {
    submitLoginForm() {
      this.$refs.authForm.validate();
      this.$nextTick(() => {
        if (!this.validForm) {
          this.loading = false;
          return;
        }
        this.loading = true;
        const formData = new FormData();
        formData.append("username", this.email.toLowerCase());
        formData.append("password", this.password);
        this.setMessage("");
        this.setError("");
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
    },
    submitForgotPasswordForm() {
      this.$refs.authForm.validate();
      this.$nextTick(() => {
        if (!this.validForm) {
          this.loading = false;
          return;
        }
        this.loading = true;
        const formData = new FormData();
        formData.append("email", this.email);
        this.setMessage("");
        this.setError("");
        this.$store.dispatch(`auth/${FORGOT_PASSWORD}`, formData).then(
          () => {
            this.loading = false;
          },
          () => {
            this.loading = false;
          }
        );
      });
    },

    submitResetPasswordForm() {
      this.$refs.authForm.validate();
      this.$nextTick(() => {
        if (!this.validForm) {
          this.loading = false;
          return;
        }
        this.loading = true;
        this.setMessage("");
        this.setError("");
        const token = this.$route.query.token;
        this.$store
          .dispatch(`auth/${RESET_PASSWORD}`, {
            token,
            new_password: this.password
          })
          .then(
            () => {
              this.loading = false;
              this.token = token;
              this.$router.push({ name: "login" });
            },
            () => {
              this.loading = false;
            }
          );
      });
    },
    submitCreateAccountForm() {},
    clear() {
      this.$refs.authForm.reset();
      if (this.token) {
        const decodedToken = jwt_decode(this.token);
        this.email = decodedToken.sub;
      } else {
        this.email = "";
      }
      this.token = "";
      this.password = "";
      this.confirmPassword = "";
      this.loading = false;
      this.validForm = false;
      this.password_visibility = false;
      this.confirmPassword_visibility = false;
    },
    ...mapMutations("auth", { setError: SET_ERROR, setMessage: SET_MESSAGE })
  },
  computed: {
    ...mapState({
      errors: state => state.auth.errors,
      message: state => state.auth.message
    }),
    passwordMatch() {
      return () =>
        this.password === this.confirmPassword ||
        this.$t("login.passwordMustMatch");
    }
  },
  watch: {
    // eslint-disable-next-line no-unused-vars
    $route(newRoute, oldRoute) {
      this.clear();
      if (oldRoute.name === "reset-password") {
        setTimeout(() => {
          this.setMessage("");
        }, 3000);
      } else {
        this.setMessage("");
      }
      this.setError("");
    }
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
