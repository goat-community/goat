<template>
  <!-- Hide const ? Or make a readonly field -->
  <v-flex
    v-if="
      fullSchema &&
        fullSchema.const === undefined &&
        fullSchema['x-display'] !== 'hidden'
    "
    :class="propertyClass"
    :style="fullSchema['x-style'] || ''"
  >
    <slot
      :name="`prepend-${slotName}`"
      :fullKey="fullKey"
      :fullSchema="fullSchema"
      :modelWrapper="modelWrapper"
      :modelKey="modelKey"
      :model="modelWrapper[modelKey]"
      :required="required"
      :disabled="disabled"
      :rule="rules"
      :htmlDescription="htmlDescription"
    />
    <slot
      :name="slotName"
      :fullKey="fullKey"
      :fullSchema="fullSchema"
      :modelWrapper="modelWrapper"
      :modelKey="modelKey"
      :model="modelWrapper[modelKey]"
      :required="required"
      :disabled="disabled"
      :rule="rules"
      :htmlDescription="htmlDescription"
    >
      <!-- Date picker -->
      <v-menu
        v-if="
          fullSchema.type === 'string' &&
            ['date', 'date-time'].includes(fullSchema.format)
        "
        ref="menu"
        v-model="menu"
        :close-on-content-click="false"
        :nudge-right="40"
        :return-value.sync="modelWrapper[modelKey]"
        :disabled="disabled"
        transition="scale-transition"
        offset-y
        full-width
        min-width="290px"
      >
        <template v-slot:activator="{ on }">
          <v-text-field
            v-model="modelWrapper[modelKey]"
            :label="translateField(label)"
            :name="fullKey"
            :required="required"
            :rules="rules"
            :clearable="!required"
            :prepend-icon="options.icons.calendar"
            v-on="on"
          >
            <tooltip
              slot="append-outer"
              :options="options"
              :html-description="htmlDescription"
            />
          </v-text-field>
        </template>
        <v-date-picker
          v-model="modelWrapper[modelKey]"
          scrollable
          landscape
          :locale="options.locale"
        >
          <v-spacer />
          <v-btn
            text
            class="v-btn--flat"
            :style="oldFlat"
            @click="menu = false"
          >
            Cancel
          </v-btn>
          <v-btn
            text
            class="v-btn--flat primary--text"
            @click="
              $refs.menu.save(modelWrapper[modelKey]);
              change();
              input();
            "
          >
            OK
          </v-btn>
        </v-date-picker>
      </v-menu>

      <!-- Time picker -->
      <v-menu
        v-else-if="fullSchema.type === 'string' && fullSchema.format === 'time'"
        ref="menu"
        v-model="menu"
        :close-on-content-click="false"
        :nudge-right="40"
        :return-value.sync="modelWrapper[modelKey]"
        :disabled="disabled"
        transition="scale-transition"
        offset-y
        full-width
        min-width="290px"
      >
        <template v-slot:activator="{ on }">
          <v-text-field
            v-model="modelWrapper[modelKey]"
            :label="translateField(label)"
            :name="fullKey"
            :required="required"
            :rules="rules"
            :clearable="!required"
            :prepend-icon="options.icons.clock"
            readonly
            v-on="on"
          >
            <tooltip
              slot="append-outer"
              :options="options"
              :html-description="htmlDescription"
            />
          </v-text-field>
        </template>
        <v-time-picker v-model="modelWrapper[modelKey]">
          <v-spacer />
          <v-btn
            text
            class="v-btn--flat"
            :style="oldFlat"
            @click="menu = false"
          >
            Cancel
          </v-btn>
          <v-btn
            text
            class="v-btn--flat primary--text"
            @click="
              $refs.menu.save(modelWrapper[modelKey]);
              change();
              input();
            "
          >
            OK
          </v-btn>
        </v-time-picker>
      </v-menu>

      <!-- Color picking -->
      <template v-else-if="fullSchema.format === 'hexcolor'">
        <template v-if="fullSchema['x-display'] === 'color-picker'">
          <v-input
            :name="fullKey"
            :label="translateField(label)"
            :required="required"
            :rules="rules"
            :disabled="disabled"
          >
            <tooltip
              slot="append"
              :options="options"
              :html-description="htmlDescription"
            />
            &nbsp;&nbsp;
            <v-menu
              :close-on-content-click="false"
              :close-on-click="true"
              direction="bottom"
              offset-y
            >
              <template v-slot:activator="{ on }">
                <div
                  :style="`background-color: ${modelWrapper[modelKey]};`"
                  :class="
                    modelWrapper[modelKey]
                      ? 'color-picker-trigger'
                      : 'color-picker-trigger color-picker-trigger-empty'
                  "
                  v-on="on"
                />
              </template>
              <color-picker
                :value="modelWrapper[modelKey]"
                :preset-colors="options.colors.swatches"
                @input="
                  val => {
                    modelWrapper[modelKey] = val.hex;
                    input();
                    change();
                  }
                "
              />
            </v-menu>
          </v-input>
        </template>
        <v-input
          v-else
          :name="fullKey"
          :label="translateField(label)"
          :required="required"
          :rules="rules"
          :disabled="disabled"
        >
          <tooltip
            slot="append"
            :options="options"
            :html-description="htmlDescription"
          />
          &nbsp;&nbsp;
          <swatches
            v-model="modelWrapper[modelKey]"
            :disabled="disabled"
            :colors="options.colors"
            :trigger-style="{ width: '36px', height: '36px' }"
            shapes="circles"
            @input="
              input();
              change();
            "
          />
        </v-input>
      </template>

      <!-- auto-complete field on an ajax response with query -->
      <v-autocomplete
        v-else-if="fullSchema.isAutocomplete === true"
        v-model="modelWrapper[modelKey]"
        :items="translatedItems"
        :name="fullKey"
        :label="translateField(label)"
        :no-data-text="options.noDataMessage"
        :disabled="disabled"
        :required="required"
        :rules="rules"
        :clearable="!required"
        @change="change"
        @input="input"
        item-text="text"
        item-value="value"
        autocomplete="off"
      >
      </v-autocomplete>

      <!-- Select field of objects based on an enum (array or not) -->
      <template
        v-else-if="
          (fullSchema.type === 'array' &&
            fullSchema.items.enum &&
            fullSchema.items.type === 'object') ||
            (fullSchema.enum && fullSchema.type === 'object')
        "
      >
        <v-select
          v-model="modelWrapper[modelKey]"
          :items="selectItems"
          :name="fullKey"
          :label="translateField(label)"
          :item-text="translateListValues"
          :required="required"
          :rules="rules"
          :disabled="disabled"
          :clearable="!required"
          :multiple="fullSchema.type === 'array'"
          :item-value="itemKey"
          :return-object="true"
          @change="change"
          @input="input"
          autocomplete="off"
        >
        </v-select>
      </template>

      <!-- Select field of simple types based on an enum (array or simple value) -->
      <template
        v-else-if="
          (fullSchema.type === 'array' && fullSchema.items.enum) ||
            fullSchema.enum
        "
      >
        <v-select
          v-model="modelWrapper[modelKey]"
          :items="selectItems"
          :name="fullKey"
          :label="translateField(label)"
          :required="required"
          :rules="rules"
          :disabled="disabled"
          :clearable="!required"
          :multiple="fullSchema.type === 'array'"
          :item-text="translateListValues"
          @change="change"
          @input="input"
          autocomplete="off"
        >
        </v-select>
      </template>

      <!-- Long text field in a textarea -->
      <v-textarea
        v-else-if="
          fullSchema.type === 'string' &&
            fullSchema.maxLength &&
            fullSchema.maxLength > 1000 &&
            fullSchema['x-display'] !== 'single-line'
        "
        v-model="modelWrapper[modelKey]"
        :name="fullKey"
        :label="translateField(label)"
        :disabled="disabled"
        :required="required"
        :rules="rules"
        filled
        class="v-text-field--box v-text-field--enclosed"
        @change="change"
        @input="input"
      >
        <tooltip
          slot="append-outer"
          :options="options"
          :html-description="htmlDescription"
        />
      </v-textarea>

      <!-- text field displayed as password -->
      <v-text-field
        v-else-if="
          fullSchema.type === 'string' && fullSchema['x-display'] === 'password'
        "
        v-model="modelWrapper[modelKey]"
        :name="fullKey"
        :label="translateField(label)"
        :disabled="disabled"
        :required="required"
        :rules="rules"
        type="password"
        @change="change"
        @input="input"
      >
        <tooltip
          slot="append-outer"
          :options="options"
          :html-description="htmlDescription"
        />
      </v-text-field>

      <!-- Simple text field -->
      <v-text-field
        autocomplete="off"
        v-else-if="
          fullSchema.type === 'string' && fullSchema.key !== 'opening_hours'
        "
        v-model="modelWrapper[modelKey]"
        :name="fullKey"
        :label="translateField(label)"
        :disabled="disabled"
        :required="required"
        :rules="rules"
        @change="change"
        @input="input"
      >
        <tooltip
          slot="append-outer"
          :options="options"
          :html-description="htmlDescription"
        />
      </v-text-field>

      <!-- Opening Hours-->
      <v-text-field
        v-else-if="fullSchema.key === 'opening_hours'"
        v-model="modelWrapper[modelKey]"
        :name="fullKey"
        :label="translateField(label)"
        :disabled="disabled"
        :required="required"
        :rules="rules"
        @change="change"
        @input="input"
        @click="openDialog('open_dialog')"
        prepend-icon="query_builder"
      >
        <tooltip
          slot="append-outer"
          :options="options"
          :html-description="htmlDescription"
        />
      </v-text-field>
      <!-- Number fields displayed in slider -->
      <v-slider
        v-else-if="
          fullSchema['x-display'] === 'slider' &&
            (fullSchema.type === 'number' || fullSchema.type === 'integer')
        "
        v-model.number="modelWrapper[modelKey]"
        :name="fullKey"
        :label="translateField(label)"
        :min="fullSchema.minimum"
        :max="fullSchema.maximum"
        :step="
          fullSchema['x-step'] || (fullSchema.type === 'integer' ? 1 : 0.01)
        "
        :disabled="disabled"
        :required="required"
        :rules="rules"
        thumb-label
        @change="change"
        @input="input"
      >
        <tooltip
          slot="append"
          :options="options"
          :html-description="htmlDescription"
        />
      </v-slider>
      <!-- Simple number fields -->
      <v-text-field
        v-else-if="
          fullSchema.type === 'number' || fullSchema.type === 'integer'
        "
        v-model.number="modelWrapper[modelKey]"
        :name="fullKey"
        :label="translateField(label)"
        :min="fullSchema.minimum"
        :max="fullSchema.maximum"
        :step="
          fullSchema['x-step'] || (fullSchema.type === 'integer' ? 1 : 0.01)
        "
        :disabled="disabled"
        :required="required"
        :rules="rules"
        type="number"
        @change="change"
        @input="input"
        autocomplete="off"
      >
        <tooltip
          slot="append-outer"
          :options="options"
          :html-description="htmlDescription"
        />
      </v-text-field>

      <!-- Simple boolean field -->
      <v-checkbox
        v-else-if="fullSchema.type === 'boolean'"
        v-model="modelWrapper[modelKey]"
        :label="translateField(label)"
        :name="fullKey"
        :disabled="disabled"
        :required="required"
        :rules="rules"
        @change="change"
        @input="input"
      >
        <tooltip
          slot="append"
          :options="options"
          :html-description="htmlDescription"
        />
      </v-checkbox>

      <!-- Simple strings array -->
      <template
        v-else-if="
          fullSchema.type === 'array' && fullSchema.items.type === 'string'
        "
      >
        <v-combobox
          v-model="modelWrapper[modelKey]"
          :name="fullKey"
          :label="translateField(label)"
          :required="required"
          :rules="rules"
          :disabled="disabled"
          chips
          multiple
          append-icon=""
          @change="change"
          @input="input"
        >
          <tooltip
            slot="append-outer"
            :options="options"
            :html-description="htmlDescription"
          />
          <template slot="selection" slot-scope="data">
            <!-- @input is for vuetify1 and @click:close is for vuetify 2 -->
            <v-chip
              close
              @input="
                modelWrapper[modelKey].splice(data.index, 1);
                change();
                input();
              "
              @click:close="
                modelWrapper[modelKey].splice(data.index, 1);
                change();
                input();
              "
            >
              {{ data.item }}
            </v-chip>
          </template>
        </v-combobox>
      </template>

      <!-- Object sub container with properties that may include a select based on a oneOf and subparts base on a allOf -->
      <div v-else-if="fullSchema.type === 'object'">
        <v-subheader
          v-if="fullSchema.title"
          :style="foldable ? 'cursor:pointer;' : ''"
          class="mt-2"
          @click="folded = !folded"
        >
          {{ fullSchema.title }}
          &nbsp;
          <v-icon v-if="foldable && folded">
            {{ options.icons.dropdown }}
          </v-icon>
          <v-icon v-if="foldable && !folded">
            {{ options.icons.dropup }}
          </v-icon>
        </v-subheader>

        <v-slide-y-transition>
          <v-layout v-show="!foldable || !folded" row wrap class="ma-0">
            <p v-if="fullSchema.description" v-html="htmlDescription" />
            <property
              v-for="childProp in fullSchema.properties"
              :key="childProp.key"
              :schema="childProp"
              :model-wrapper="modelWrapper[modelKey]"
              :model-root="modelRoot"
              :model-key="childProp.key"
              :parent-key="fullKey + '.'"
              :required="
                !!(
                  fullSchema.required &&
                  fullSchema.required.includes(childProp.key)
                )
              "
              :options="options"
              @error="e => $emit('error', e)"
              @change="e => $emit('change', e)"
              @input="e => $emit('input', e)"
            >
              <!-- propagate slots to children, see https://gist.github.com/Loilo/73c55ed04917ecf5d682ec70a2a1b8e2 -->
              <slot v-for="(_, name) in $slots" :slot="name" :name="name" />
              <template
                v-for="(_, name) in $scopedSlots"
                :slot="name"
                slot-scope="slotData"
              >
                <slot :name="name" v-bind="slotData" />
              </template>
            </property>
          </v-layout>
        </v-slide-y-transition>
      </div>

      <!-- Tuples array sub container -->
      <div
        v-else-if="
          fullSchema.type === 'array' && Array.isArray(fullSchema.items)
        "
      >
        <v-subheader
          v-if="fullSchema.title"
          :style="foldable ? 'cursor:pointer;' : ''"
          class="mt-2"
          @click="folded = !folded"
        >
          {{ fullSchema.title }}
          &nbsp;
          <v-icon v-if="foldable && folded">
            {{ options.icons.dropdown }}
          </v-icon>
          <v-icon v-if="foldable && !folded">
            {{ options.icons.dropup }}
          </v-icon>
        </v-subheader>
        <v-slide-y-transition>
          <div v-show="!foldable || !folded">
            <p v-if="fullSchema.description" v-html="htmlDescription" />
            <property
              v-for="(child, i) in fullSchema.items"
              :key="i"
              :schema="child"
              :model-wrapper="modelWrapper[modelKey]"
              :model-root="modelRoot"
              :model-key="i"
              :parent-key="fullKey + '.'"
              :options="options"
              @error="e => $emit('error', e)"
              @change="e => $emit('change', e)"
              @input="e => $emit('input', e)"
            >
              <!-- propagate slots to children, see https://gist.github.com/Loilo/73c55ed04917ecf5d682ec70a2a1b8e2 -->
              <slot v-for="(_, name) in $slots" :slot="name" :name="name" />
              <template
                v-for="(_, name) in $scopedSlots"
                :slot="name"
                slot-scope="slotData"
              >
                <slot :name="name" v-bind="slotData" />
              </template>
            </property>
          </div>
        </v-slide-y-transition>
      </div>

      <!-- Dynamic size array of complex types sub container -->
      <div v-else-if="fullSchema.type === 'array'">
        <v-layout row class="mt-2 mb-1 pr-1">
          <v-subheader>{{ label }}</v-subheader>
          <v-btn
            v-if="!disabled && !(fromUrl || fullSchema.fromData)"
            fab
            small
            color="primary"
            @click="
              modelWrapper[modelKey].push(
                fullSchema.items.default || defaultValue(fullSchema.items)
              );
              change();
              input();
            "
          >
            <v-icon>{{ options.icons.add }}</v-icon>
          </v-btn>
          <v-spacer />
          <tooltip :options="options" :html-description="htmlDescription" />
        </v-layout>

        <v-container
          v-if="modelWrapper[modelKey] && modelWrapper[modelKey].length"
          grid-list-md
          class="pt-0 px-2"
        >
          <v-layout row wrap class="ma-0">
            <draggable
              v-model="modelWrapper[modelKey]"
              handle=".handle"
              style="width: 100%;"
            >
              <v-flex
                v-for="(itemModel, i) in modelWrapper[modelKey]"
                :key="i"
                xs12
              >
                <v-card class="array-card">
                  <v-card-title primary-title class="pa-0">
                    <v-btn
                      v-if="!disabled && fullSchema['x-sortable'] !== false"
                      icon
                      class="handle"
                    >
                      <v-icon>{{ options.icons.reorder }}</v-icon>
                    </v-btn>
                    <span v-if="itemTitle && modelWrapper[modelKey][i]">{{
                      modelWrapper[modelKey][i][itemTitle]
                    }}</span>
                    <v-spacer />
                    <v-btn
                      v-if="!disabled && !(fromUrl || fullSchema.fromData)"
                      icon
                      color="warning"
                      @click="
                        modelWrapper[modelKey].splice(i, 1);
                        change();
                        input();
                      "
                    >
                      <v-icon>{{ options.icons.delete }}</v-icon>
                    </v-btn>
                  </v-card-title>
                  <v-card-text>
                    <property
                      :schema="fullSchema.items"
                      :model-wrapper="modelWrapper[modelKey]"
                      :model-root="modelRoot"
                      :model-key="i"
                      :parent-key="`${fullKey}.`"
                      :options="options"
                      @error="e => $emit('error', e)"
                      @change="e => $emit('change', e)"
                      @input="e => $emit('input', e)"
                    >
                      <!-- propagate slots to children, see https://gist.github.com/Loilo/73c55ed04917ecf5d682ec70a2a1b8e2 -->
                      <slot
                        v-for="(_, name) in $slots"
                        :slot="name"
                        :name="name"
                      />
                      <template
                        v-for="(_, name) in $scopedSlots"
                        :slot="name"
                        slot-scope="slotData"
                      >
                        <slot :name="name" v-bind="slotData" />
                      </template>
                    </property>
                  </v-card-text>
                </v-card>
              </v-flex>
            </draggable>
          </v-layout>
        </v-container>
      </div>

      <p v-else-if="options.debug">
        Unsupported type "{{ fullSchema.type }}" - {{ fullSchema }}
      </p>
    </slot>
    <slot
      :name="`append-${slotName}`"
      :fullKey="fullKey"
      :fullSchema="fullSchema"
      :modelWrapper="modelWrapper"
      :modelKey="modelKey"
      :model="modelWrapper[modelKey]"
      :required="required"
      :disabled="disabled"
      :rule="rules"
      :htmlDescription="htmlDescription"
    />
  </v-flex>
</template>

<script>
import Tooltip from "./Tooltip.vue";
import schemaUtils from "../utils/schema";
import selectUtils from "../utils/select";

export default {
  name: "Property",
  components: { Tooltip },
  props: [
    "schema",
    "modelWrapper",
    "modelRoot",
    "modelKey",
    "parentKey",
    "required",
    "options"
  ],
  data() {
    return {
      ready: false,
      menu: false,
      rawSelectItems: null,
      selectItems: null,
      q: "",
      currentOneOf: null,
      showCurrentOneOf: true,
      fromUrlParams: {},
      loading: false,
      folded: true,
      showColorPicker: false,
      subModels: {}, // a container for objects from root oneOfs and allOfs
      // maintain vuetify1 compatibility without triggering warning on flat attribute for vuetify 2
      oldFlat: `
        background-color: none !important;
        border-color: none !important;
        `
    };
  },
  computed: {
    fullSchema() {
      return schemaUtils.prepareFullSchema(
        this.schema,
        this.modelWrapper,
        this.modelKey
      );
    },
    htmlDescription() {
      return null;
    },
    fullKey() {
      return (this.parentKey + this.modelKey).replace("root.", "");
    },
    label() {
      return (
        this.fullSchema.title ||
        (typeof this.modelKey === "string" ? this.modelKey : "")
      );
    },
    rules() {
      return schemaUtils.getRules(
        this.fullSchema,
        this.required,
        this.options,
        this.modelWrapper
      );
    },
    fromUrl() {
      return !!(
        this.fullSchema["x-fromUrl"] &&
        this.fullSchema["x-fromUrl"].indexOf("{q}") === -1
      );
    },
    fromUrlWithQuery() {
      return !!(
        this.fullSchema["x-fromUrl"] &&
        this.fullSchema["x-fromUrl"].indexOf("{q}") !== -1
      );
    },
    fromUrlKeys() {
      // Look for variable parts in the URL used to fetch data
      return null;
    },
    itemKey() {
      return this.fullSchema["x-itemKey"] || "key";
    },
    itemTitle() {
      return this.fullSchema["x-itemTitle"] || "title";
    },
    itemIcon() {
      return (
        this.fullSchema["x-itemIcon"] ||
        (this.fullSchema["x-display"] === "icon" ? this.itemKey : null)
      );
    },
    disabled() {
      return this.options.disableAll;
    },
    foldable() {
      return (
        this.options.autoFoldObjects && this.parentKey && this.fullSchema.title
      );
    },
    oneOfConstProp() {
      if (!this.fullSchema.oneOf) return;
      const props = this.fullSchema.oneOf[0].properties;
      const key = Object.keys(props).find(p => !!props[p].const);
      if (!key) return;
      return {
        ...props[key],
        key,
        htmlDescription: ""
      };
    },
    oneOfRequired() {
      return !!(
        this.oneOfConstProp &&
        this.fullSchema &&
        this.fullSchema.required &&
        this.fullSchema.required.find(r => r === this.oneOfConstProp.key)
      );
    },
    oneOfRules() {
      const rules = [];
      if (this.oneOfRequired)
        rules.push(
          val =>
            (val !== undefined && val !== null && val !== "") ||
            this.options.requiredMessage
        );
      return rules;
    },
    oneOfSelect() {
      return schemaUtils.isOneOfSelect(this.fullSchema);
    },
    slotName() {
      return this.fullSchema["x-display"] &&
        this.fullSchema["x-display"].startsWith("custom-")
        ? this.fullSchema["x-display"]
        : this.fullKey;
    },
    propertyClass() {
      const cleanKey = this.fullKey.replace(/\./g, "-").replace(/[0-9]/g, "");
      return `vjsf-property vjsf-property-${cleanKey} xs12 ${this.fullSchema[
        "x-class"
      ] || ""}`;
    },
    translatedItems() {
      const translatedItems = [];
      if (Array.isArray(this.selectItems) && this.selectItems.length > 0) {
        this.selectItems.forEach(item => {
          translatedItems.push({
            value: item,
            text: this.translateListValues(item)
          });
        });
      }
      return translatedItems;
    }
  },
  watch: {
    q() {
      // This line prevents reloading the list just after selecting an item in an auto-complete
      if (
        this.modelWrapper[this.modelKey] &&
        this.modelWrapper[this.modelKey][this.itemTitle] === this.q
      )
        return;
      this.fetchSelectItems();
    },
    fullSchema: {
      handler() {
        if (
          this.fullSchema &&
          JSON.stringify(this.fullSchema) !== this.lastFullSchema
        ) {
          this.lastFullSchema = JSON.stringify(this.fullSchema);
          this.initFromSchema();
          this.cleanUpExtraProperties();
          this.applySubModels();
          this.ready = true;
        }
      },
      immediate: true
    },
    currentOneOf() {
      // use this boolean to force removing then re-creating the object property
      // base on the currentOneOf sub schema. If we don't the component is reused and reactivity creates some difficult bugs.
      this.showCurrentOneOf = false;
      this.$nextTick(() => {
        this.showCurrentOneOf = true;
        if (!this.currentOneOf) this.$set(this.subModels, "currentOneOf", {});
        this.cleanUpExtraProperties();
      });
    },
    subModels: {
      handler() {
        this.cleanUpExtraProperties();
        this.applySubModels();
      },
      deep: true
    },
    rawSelectItems: {
      handler() {
        this.updateSelectItems();
      },
      immediate: true
    }
  },
  methods: {
    openDialog(e) {
      this.$emit("input", e);
    },
    translateField(field) {
      const layerName = this.schema.layerName;
      const canTranslate = this.$te(
        `dynamicFields.attributes.${layerName}.${field}`
      );
      if (canTranslate) {
        return this.$t(`dynamicFields.attributes.${layerName}.${field}`);
      } else {
        return field;
      }
    },
    translateListValues(value) {
      let layerName = this.schema.layerName;
      let path = `dynamicFields.listValues.`;
      if (layerName === "poi") {
        layerName = "pois";
        path = ``;
      }
      const canTranslate = this.$te(`${path}${layerName}.${value}`);
      if (canTranslate) {
        return this.$t(`${path}${layerName}.${value}`);
      } else {
        return value;
      }
    },
    updateSelectItems() {
      const selectItems = selectUtils.getSelectItems(
        this.rawSelectItems,
        this.fullSchema,
        this.modelWrapper,
        this.modelKey,
        this.itemKey
      );
      if (this.fullSchema["x-display"] === "list") {
        selectUtils.fillList(
          this.fullSchema,
          this.modelWrapper,
          this.modelKey,
          selectItems,
          this.itemKey
        );
      } else {
        selectUtils.fillSelectItems(
          this.fullSchema,
          this.modelWrapper,
          this.modelKey,
          selectItems,
          this.itemKey
        );
      }

      // we check for actual differences in order to prevent infinite loops
      if (JSON.stringify(selectItems) !== JSON.stringify(this.selectItems)) {
        this.selectItems = selectItems;
      }
    },
    change() {
      this.updateSelectItems();
      this.$emit("change", {
        key: this.fullKey.replace(/allOf-([0-9]+)\./g, ""),
        model: this.modelWrapper[this.modelKey]
      });
    },
    input() {
      this.$emit("input", {
        key: this.fullKey.replace(/allOf-([0-9]+)\./g, ""),
        model: this.modelWrapper[this.modelKey]
      });
    },
    defaultValue(schema) {
      if (
        schema.type === "object" &&
        !schema["x-fromUrl"] &&
        !schema["x-fromData"] &&
        !schema.enum
      )
        return {};
      if (schema.type === "array") return [];
      return null;
    },
    fetchSelectItems() {
      if (!this.options.httpLib)
        return this.$emit("error", "No http lib found to perform ajax request");
      let url = this.fullSchema["x-fromUrl"].replace("{q}", this.q || "");
      for (const key of this.fromUrlKeys) {
        // URL parameters are incomplete
        if (this.fromUrlParams[key] === undefined) return;
        else url = url.replace(`{${key}}`, this.fromUrlParams[key]);
      }
      this.loading = true;
      this.options.httpLib
        .get(url)
        .then(res => {
          const body = res.data || res.body;
          const items = this.fullSchema["x-itemsProp"]
            ? body[this.fullSchema["x-itemsProp"]]
            : body;
          if (!Array.isArray(items))
            throw new Error(`Result of http fetch ${url} is not an array`);
          this.rawSelectItems = items;
          this.loading = false;
        })
        .catch(err => {
          this.$emit("error", err.message);
          this.loading = false;
        });
    },
    cleanUpExtraProperties() {
      // cleanup extra properties
      if (
        this.fullSchema.type === "object" &&
        this.fullSchema.properties &&
        Object.keys(this.fullSchema.properties).length &&
        this.modelWrapper[this.modelKey]
      ) {
        Object.keys(this.modelWrapper[this.modelKey]).forEach(key => {
          if (!this.fullSchema.properties.find(p => p.key === key)) {
            delete this.modelWrapper[this.modelKey][key];
          }
        });
      }
    },
    applySubModels() {
      Object.keys(this.subModels).forEach(subModel => {
        Object.keys(this.subModels[subModel]).forEach(key => {
          if (
            this.modelWrapper[this.modelKey][key] !==
            this.subModels[subModel][key]
          ) {
            this.$set(
              this.modelWrapper[this.modelKey],
              key,
              this.subModels[subModel][key]
            );
          }
        });
      });
    },
    initFromSchema() {
      let model = this.modelWrapper[this.modelKey];

      // Manage default values
      if (model === undefined) {
        model = this.defaultValue(this.fullSchema);
        if (this.fullSchema.default !== undefined)
          model = JSON.parse(JSON.stringify(this.fullSchema.default));
      }
      // const always wins
      if (this.fullSchema.const !== undefined) model = this.fullSchema.const;

      // color pickers do not like null values
      if (
        this.fullSchema.type === "string" &&
        this.fullSchema.format === "hexcolor"
      )
        model = model || "";

      // Case of a select based on ajax query
      if (this.fromUrl) this.fetchSelectItems();
      // Case of select based on an enum
      if (
        (this.fullSchema.type === "array" && this.fullSchema.items.enum) ||
        this.fullSchema.enum
      ) {
        this.rawSelectItems =
          this.fullSchema.type === "array"
            ? this.fullSchema.items.enum
            : this.fullSchema.enum;
      }
      // Case of select based on a oneof on simple types
      if (this.oneOfSelect) {
        this.rawSelectItems = (this.fullSchema.type === "array"
          ? this.fullSchema.items
          : this.fullSchema
        ).oneOf.map(item => ({
          ...item,
          [this.itemKey]: item.const || (item.enum && item.enum[0]),
          [this.itemTitle]: item.title
        }));
      }
      // Case of an auto-complete field already defined
      if (
        this.fromUrlWithQuery &&
        model &&
        model[this.itemTitle] !== undefined
      ) {
        this.q = model[this.itemTitle];
      }
      // Case of a select based on an array somewhere in the data
      if (this.fullSchema["x-fromData"]) {
        this.$watch(
          "modelRoot." + this.fullSchema["x-fromData"],
          val => {
            this.rawSelectItems = val;
          },
          { immediate: true }
        );
      }
      // Watch the dynamic parts of the URL used to fill the select field
      if (this.fromUrlKeys) {
        this.fromUrlKeys.forEach(key => {
          if (key.startsWith("context.")) {
            this.$watch(
              "options." + key,
              val => {
                this.fromUrlParams[key] = val;
                this.fetchSelectItems();
              },
              { immediate: true }
            );
          } else {
            this.$watch(
              "modelRoot." + key,
              val => {
                this.fromUrlParams[key] = val;
                this.fetchSelectItems();
              },
              { immediate: true }
            );
          }
        });
      }

      // Init subModels for allOf subschemas
      if (this.fullSchema.type === "object" && this.fullSchema.allOf) {
        this.fullSchema.allOf.forEach((allOf, i) => {
          this.$set(
            this.subModels,
            "allOf-" + i,
            JSON.parse(JSON.stringify(model))
          );
        });
      }

      // Case of a sub type selection based on a oneOf
      this.currentOneOf = null;
      if (
        this.fullSchema.type === "object" &&
        this.fullSchema.oneOf &&
        !this.currentOneOf &&
        this.oneOfConstProp
      ) {
        if (model && model[this.oneOfConstProp.key]) {
          this.currentOneOf = this.fullSchema.oneOf.find(
            item =>
              item.properties[this.oneOfConstProp.key].const ===
              model[this.oneOfConstProp.key]
          );
        } else if (this.fullSchema.default) {
          this.currentOneOf = this.fullSchema.oneOf.find(
            item =>
              item.properties[this.oneOfConstProp.key].const ===
              this.fullSchema.default[this.oneOfConstProp.key]
          );
        }
      }

      // Init subModel for current oneOf
      if (this.currentOneOf) {
        this.$set(
          this.subModels,
          "currentOneOf",
          JSON.parse(JSON.stringify(model))
        );
      } else {
        this.$set(this.subModels, "currentOneOf", {});
      }

      // Cleanup arrays of empty items
      if (this.fullSchema.type === "array") {
        model = model.filter(item => ![undefined, null].includes(item));
      }

      this.$set(this.modelWrapper, this.modelKey, model);
    }
  }
};
</script>

<style lang="css">
.vjsf-property .array-card .v-card__text {
  padding: 6px 16px 0 16px;
}
.vjsf-property .array-card .v-card__actions {
  padding: 0 16px 6px 16px;
}

.vjsf-property .v-input--selection-controls {
  margin-top: 0;
}

.vjsf-tooltip p:last-child {
  margin-bottom: 0;
}

.vjsf-property .color-picker-trigger {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  cursor: pointer;
  display: inline-block;
  border: 2px solid #ccc;
}

.vjsf-property .color-picker-trigger-empty {
  background: linear-gradient(
    to top right,
    transparent 0,
    transparent calc(50% - 2.4px),
    #de080a 50%,
    transparent calc(50% + 2.4px),
    transparent
  );
}
</style>
