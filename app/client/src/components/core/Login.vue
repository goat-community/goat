<template>
  <v-flex xs12 sm8 md4>
    <v-card flat>
      <v-card-title primary-title>
        <span class="title font-weight-regular">Login</span>
      </v-card-title>
      <v-card-text class="pr-16 pl-16 pt-0 pb-0">
        <v-divider></v-divider>
      </v-card-text>
      <v-card-text>
        <v-form ref="login" lazy-validation>
          <v-text-field
            prepend-icon="person"
            name="username"
            label="Username"
            type="text"
            :rules="rules.username"
            required
          ></v-text-field>
          <v-text-field
            prepend-icon="lock"
            name="password"
            label="Password"
            id="password"
            :rules="rules.password"
            type="password"
            required
          ></v-text-field>
        </v-form>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn class="white--text" @click="login" color="green">Login</v-btn>
      </v-card-actions>
    </v-card>
  </v-flex>
</template>

<script>
export default {
  data: () => ({
    rules: {
      username: [v => !!v || "Username is required"],
      password: [v => !!v || "Password is required"]
    }
  }),
  components: {},
  computed: {},
  methods: {
    login() {
      if (this.$refs.login.validate()) {
        console.log("init login...");
      }
    }
  },
  mounted() {}
};
</script>
