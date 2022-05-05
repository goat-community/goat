<template>
  <v-app id="inspire">
    <v-content>
      <v-container fluid fill-height class="pa-0">
        <div style="width: 100%;">
          <div class="carousel-widget-wrapper">
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
          </div>
          <div class="auth-panel-wrapper">
            <vue-scroll>
              <div class="pa-4">
                <v-row
                  class="ma-0"
                  justify="center"
                  align="center"
                  style="padding-top:60px;padding-bottom:60px;padding-left:35px;padding-right:35px;min-width:300px;"
                >
                  <img src="img/goat_standard.svg" height="40px" />
                </v-row>

                <v-alert
                  colored-border
                  border="left"
                  class="ma-2 mx-6"
                  v-if="errors"
                  elevation="2"
                  type="error"
                >
                  {{ errors }}
                </v-alert>
                <v-alert
                  v-if="message"
                  colored-border
                  border="left"
                  elevation="2"
                  class="ma-2 mx-6"
                  icon="fa-solid fa-circle-check"
                  color="#2BB381"
                >
                  {{ message }}
                </v-alert>
                <!-- SIGN IN  -->
                <v-card-text class="mb-12" v-if="$route.name === 'login'">
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
                    <router-link
                      style="z-index:2;color:#2BB381;text-decoration:none;"
                      to="/register"
                      class="ml-2"
                    >
                      {{ $t("login.signUp") }}
                    </router-link>
                  </v-row>
                </v-card-text>

                <!-- SIGN UP   -->
                <v-card-text
                  class="mb-12"
                  v-if="$route.name === 'register-demo'"
                >
                  <h3 class="mb-0 pb-0 ml-2 mb-4 font-weight-regular">
                    {{ $t("login.register").toUpperCase() }}
                  </h3>
                  <v-form
                    ref="authForm"
                    v-model="validForm"
                    @keyup.native.enter="submitRegisterForm"
                    class="mx-2"
                  >
                    <v-text-field
                      v-model="name"
                      outlined
                      name="name"
                      :label="$t('login.firstName')"
                      type="text"
                      :disabled="loading"
                      :rules="fieldRequired"
                    >
                    </v-text-field>
                    <v-text-field
                      v-model="surname"
                      outlined
                      name="surname"
                      :label="$t('login.lastName')"
                      type="text"
                      :disabled="loading"
                      validate-on-blur
                      :rules="fieldRequired"
                    >
                    </v-text-field>
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
                    <v-select
                      v-model="occupation"
                      :items="professions"
                      :item-text="
                        item => $t(`login.professionList.${item.name}`)
                      "
                      item-value="name"
                      :label="$t('login.profession')"
                      outlined
                      :disabled="loading"
                      validate-on-blur
                      :rules="fieldRequired"
                    />
                    <v-select
                      v-model="domain"
                      :items="domains"
                      :item-text="item => $t(`login.domainList.${item.name}`)"
                      item-value="name"
                      :label="$t('login.domain')"
                      outlined
                      :disabled="loading"
                      validate-on-blur
                      :rules="fieldRequired"
                    />
                    <v-row class="mx-2 mt-n5 pt-0">
                      <v-spacer></v-spacer>
                      <router-link
                        style="z-index:2;color:#2BB381;text-decoration:none;"
                        to="/login"
                        >{{ $t("login.backToLogin") }}</router-link
                      >
                    </v-row>
                    <v-checkbox
                      class="mt-3"
                      color="#2BB381"
                      :rules="fieldRequired"
                      v-model="agreedTerms"
                    >
                      <template v-slot:label>
                        {{ $t("login.agreeTerms") }} &nbsp;
                        <a
                          target="_blank"
                          style="color:#2BB381;text-decoration:none;"
                          href="https://plan4better.de/en/privacy/"
                          @click.stop
                        >
                          <span>{{ $t(`login.termsAndConditions`) }}</span>
                        </a>
                      </template>
                    </v-checkbox>
                    <v-checkbox
                      color="#2BB381"
                      class="mt-n1"
                      v-model="newsletter"
                    >
                      <template v-slot:label>
                        {{ $t("login.newsletter") }}
                      </template>
                    </v-checkbox>
                  </v-form>

                  <v-row class="mt-5 mx-0" align="center">
                    <v-col class="text-center">
                      <v-btn
                        height="50px"
                        width="100%"
                        class="text-xs-center white--text"
                        color="#2BB381"
                        :loading="loading"
                        @click="submitRegisterForm"
                      >
                        {{ $t("login.register") }}
                      </v-btn>
                    </v-col>
                  </v-row>
                </v-card-text>

                <!-- FORGOT-PASSWORD  -->
                <v-card-text
                  class="mb-12"
                  v-if="$route.name === 'forgot-password'"
                >
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

                <!-- RESET-PASSWORD -->
                <v-card-text
                  class="mb-12"
                  v-if="$route.name === 'reset-password'"
                >
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

                <!-- BOTTOM -->
                <v-row class="footer">
                  <div class="mx-3">
                    <a href="https://plan4better.de/" target="_blank">
                      <img
                        style="cursor:pointer;"
                        src="img/plan4better_standard.svg"
                        height="30px"
                      />
                    </a>
                    <v-spacer></v-spacer>
                  </div>
                  <v-spacer></v-spacer>
                  <div>
                    <language></language>
                  </div>
                </v-row>
              </div>
            </vue-scroll>
          </div>
        </div>
        <v-layout justify-center>
          <v-row>
            <v-col cols="8" class="pa-0"> </v-col>

            <v-col class="elevation-5" cols="4"> </v-col>
          </v-row>
        </v-layout>
      </v-container>
    </v-content>
  </v-app>
</template>

<script>
import {
  LOGIN,
  FORGOT_PASSWORD,
  RESET_PASSWORD,
  CREATE_USER,
  ACTIVATE_ACCOUNT
} from "../store/actions.type";
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
      name: "",
      surname: "",
      email: "",
      password: "",
      confirmPassword: "",
      occupation: "",
      domain: "",
      professions: [
        { name: "student" },
        { name: "employee" },
        { name: "self-employed" },
        { name: "other" }
      ],
      domains: [
        { name: "transport_planning" },
        { name: "urban_planning" },
        { name: "gis" },
        { name: "architecture" },
        { name: "location_planning" },
        { name: "civil_engineer" },
        { name: "political_decision_maker" },
        { name: "other" }
      ],
      agreedTerms: false,
      newsletter: false,
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
        v => !!v || this.$t("login.fieldRequired"),
        v => v.length >= 4 || this.$t("login.maxFourChar")
      ],
      emailRules: [
        v => !!v || this.$t("login.fieldRequired"),
        v =>
          /^(([^<>()[\]\\.,;:\s@']+(\.[^<>()\\[\]\\.,;:\s@']+)*)|('.+'))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/.test(
            v
          ) || this.$t("login.mailValid")
      ],
      fieldRequired: [v => !!v || this.$t("login.fieldRequired")],
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
    submitRegisterForm() {
      this.$refs.authForm.validate();
      this.$nextTick(() => {
        if (!this.validForm) {
          this.loading = false;
          return;
        }
        this.loading = true;
        this.setMessage("");
        this.setError("");
        this.$store
          .dispatch(`auth/${CREATE_USER}`, {
            name: this.name,
            surname: this.surname,
            email: this.email,
            password: this.password,
            occupation: this.occupation,
            domain: this.domain,
            newsletter: this.newsletter,
            language_preference: this.$i18n.locale
          })
          .then(
            () => {
              this.setMessage(this.$t("login.activateAccount"));
              this.$router.push({ name: "login" });
              this.loading = false;
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
    clear() {
      this.$refs.authForm.reset();
      if (this.token) {
        const decodedToken = jwt_decode(this.token);
        this.email = decodedToken.sub;
      } else {
        this.email = "";
      }
      this.name = "";
      this.surname = "";
      this.token = "";
      this.password = "";
      this.confirmPassword = "";
      this.loading = false;
      this.validForm = false;
      this.password_visibility = false;
      this.confirmPassword_visibility = false;
      this.profession = "";
      this.domain = "";
      this.agreedTerms = false;
      this.newsletter = false;
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
      if (
        oldRoute.name === "reset-password" ||
        oldRoute.name === "register-demo"
      ) {
        setTimeout(() => {
          this.setMessage("");
        }, 5000);
      } else {
        this.setMessage("");
      }
      this.setError("");
    }
  },
  mounted() {
    if (this.$route.name === "activate-account") {
      const token = this.$route.query.token;
      this.loading = true;
      this.$router.push({ name: "login" });
      this.$store
        .dispatch(`auth/${ACTIVATE_ACCOUNT}`, {
          token: token
        })
        .then(
          () => {
            this.loading = false;
            this.setMessage(this.$t("login.accountActivated"));
            setTimeout(() => {
              this.setMessage("");
            }, 3000);
          },
          () => {
            this.loading = false;
          }
        );
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

.carousel-widget-wrapper {
  overflow: hidden;
  width: calc((100%) - 400px);
  height: 100%;
}

.auth-panel-wrapper {
  position: absolute;
  right: 0;
  top: 0;
  overflow-y: auto;
  height: 100vh;
  width: 400px;
  background: #fff;
  box-shadow: -23px 0 50px 0 rgb(24 24 25 / 75%);
}

.footer {
  position: absolute;
  bottom: 20px;
  width: 95%;
}
</style>
