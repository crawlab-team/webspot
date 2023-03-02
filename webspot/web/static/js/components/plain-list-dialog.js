const {ref, computed, watch} = Vue;
const {ElMessage} = ElementPlus;

export default {
  name: 'ListDialog',
  props: {
    visible: Boolean,
    result: {
      type: Object,
      default: () => {
        return {};
      }
    },
  },
  setup(props, {emit}) {
    const activeTabName = ref('overview');
    const columns = computed(() => {
      if (!props.result) return [];
      return props.result.fields.map(f => {
        const {data} = props.result;
        // get all the data for each column
        const arr = data.map(d => d[f.name]).filter(d => d !== undefined);
        // add the label of each column
        arr.push(f.name);
        f.width = getMaxLength(arr) + 60;
        return {
          ...f,
          key: f.name,
          label: f.name,
          width: f.width,
        };
      });
    });
    const dialogVisible = ref(false);
    watch(() => props.visible, () => {
      dialogVisible.value = props.visible;
    });
    const onDialogClose = () => {
      emit('close');
    };
    const selectorType = ref('css');

    const onCopy = async (text) => {
      await navigator.clipboard.writeText(text);
      await ElMessage({message: 'Copied to clipboard', duration: 1000});
    };

    const getMaxLength = (arr) => {
      return arr.reduce((acc, item) => {
        if (item) {
          let calcLen = getTextWidth(item);
          if (acc < calcLen) {
            acc = calcLen;
          }
        }
        return acc;
      }, 0);
    };

    // use the span tag to wrap the content and then calculate the width of the span
    const getTextWidth = (str) => {
      let width = 0;
      let html = document.createElement('span');
      html.innerText = str;
      html.className = 'getTextWidth';
      document.querySelector('body').appendChild(html);
      width = document.querySelector('.getTextWidth').offsetWidth;
      document.querySelector('.getTextWidth').remove();
      return width;
    };

    return {
      dialogVisible,
      onDialogClose,
      activeTabName,
      columns,
      selectorType,
      onCopy,
      getMaxLength,
      getTextWidth,
    };
  },
  template: `
<el-dialog v-if="result.detector === 'plain_list'" :title="result.name" v-model="dialogVisible" @close="onDialogClose" width="80%">
  <el-tabs v-model="activeTabName">
    <el-tab-pane label="Overview" name="overview">
      <el-form v-if="result" label-width="180px">
        <el-form-item label="Score">
          <el-tooltip content="Score (Overall)">
            <el-tag type="primary" style="margin-right: 5px">
              <i class="fa fa-star"></i>
              {{ result.score.toFixed(2) }}
            </el-tag>
          </el-tooltip>
          <el-tooltip content="Sub-Score (Text Richness)">
            <el-tag type="info" style="margin-right: 5px">
              <i class="fa fa-font"></i>
              {{ result.scores.text_richness.toFixed(2) }}
            </el-tag>
          </el-tooltip>
          <el-tooltip content="Sub-Score (Complexity)">
            <el-tag type="info" style="margin-right: 5px">
              <i class="fa fa-code-fork"></i>
              {{ result.scores.complexity.toFixed(2) }}
            </el-tag>
          </el-tooltip>
          <el-tooltip content="Sub-Score (Item Count)">
            <el-tag type="info" style="margin-right: 5px">
              <i class="fa fa-list"></i>
              {{ result.scores.item_count.toFixed(2) }}
            </el-tag>
          </el-tooltip>
        </el-form-item>
        <el-form-item label="Selector Type">
          <el-radio-group v-model="selectorType">
            <el-radio label="css">CSS</el-radio>
            <el-radio label="xpath" disabled>XPath</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="List">
          <el-tag type="primary">{{ result.selectors.list.selector }}</el-tag>
          <el-icon style="margin-left:5px;cursor:pointer;" @click="() => onCopy(result.selectors.list.selector)">
            <i class="fa fa-paste"></i>
          </el-icon>
        </el-form-item>
        <el-form-item label="Items">
          <el-tag type="primary">{{ result.selectors.items.selector }}</el-tag>
          <el-icon style="margin-left:5px;cursor:pointer;" @click="() => onCopy(result.selectors.items.selector)">
            <i class="fa fa-paste"></i>
          </el-icon>
        </el-form-item>
        <el-form-item label="Items (Full Path)">
          <el-tag type="primary">{{ result.selectors.full_items.selector }}</el-tag>
          <el-icon style="margin-left:5px;cursor:pointer;" @click="() => onCopy(result.selectors.full_items.selector)">
            <i class="fa fa-paste"></i>
          </el-icon>
        </el-form-item>
      </el-form>
    </el-tab-pane>

    <el-tab-pane label="Data" name="data">
      <el-table v-if="result" :data="result.data" :cell-style="{padding: '5px 10px'}" border>
        <el-table-column
          v-for="column in columns"
          :key="column.key"
          :prop="column.key"
          :label="column.label"
          :width="column.width"
        >
          <template #default="scope">
            <template v-if="column.type === 'text'">
              {{ scope.row[column.key] }}
            </template>
            <template v-else-if="column.type === 'link_url'">
              <a :href="scope.row[column.key]" target="_blank">{{ scope.row[column.key] }}</a>
            </template>
            <template v-else-if="column.type === 'image_url'">
              <img :src="scope.row[column.key]" style="max-width: 100px; max-height: 100px;" />
            </template>
            <template v-else>
              {{ scope.row[column.key] }}
            </template>
          </template>
        </el-table-column>
      </el-table>
    </el-tab-pane>
  </el-tabs>
</el-dialog>
`
};