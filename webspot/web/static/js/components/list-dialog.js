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
      },
    },
  },
  setup(props, {emit}) {
    const activeTabName = ref('overview');
    const columns = computed(() => {
      if (!props.result) return [];
      return props.result.extract_rules_css.fields.map(f => {
        return {
          key: f.name,
          label: f.name,
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

    return {
      dialogVisible,
      onDialogClose,
      activeTabName,
      columns,
      selectorType,
      onCopy,
    };
  },
  template: `
<el-dialog :title="result.name" v-model="dialogVisible" @close="onDialogClose" width="80%">
  <el-tabs v-model="activeTabName">
    <el-tab-pane label="Overview" name="overview">
      <el-form v-if="result" label-width="180px">
        <el-form-item label="Score">
          <el-tooltip content="Score (Overall)">
            <el-tag type="primary" style="margin-right: 5px">
              <i class="fa fa-star"></i>
              {{ result.stats.score.toFixed(2) }}
            </el-tag>
          </el-tooltip>
          <el-tooltip content="Sub-Score (Text Richness)">
            <el-tag type="info" style="margin-right: 5px">
              <i class="fa fa-font"></i>
              {{ result.stats.scores.text_richness.toFixed(2) }}
            </el-tag>
          </el-tooltip>
          <el-tooltip content="Sub-Score (Complexity)">
            <el-tag type="info" style="margin-right: 5px">
              <i class="fa fa-code-fork"></i>
              {{ result.stats.scores.complexity.toFixed(2) }}
            </el-tag>
          </el-tooltip>
          <el-tooltip content="Sub-Score (Item Count)">
            <el-tag type="info" style="margin-right: 5px">
              <i class="fa fa-list"></i>
              {{ result.stats.scores.item_count.toFixed(2) }}
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
          <el-tag type="primary">{{ result.extract_rules_css.list }}</el-tag>
          <el-icon style="margin-left:5px;cursor:pointer;" @click="() => onCopy(result.extract_rules_css.list)">
            <i class="fa fa-paste"></i>
          </el-icon>
        </el-form-item>
        <el-form-item label="Items">
          <el-tag type="primary">{{ result.extract_rules_css.items }}</el-tag>
          <el-icon style="margin-left:5px;cursor:pointer;" @click="() => onCopy(result.extract_rules_css.items)">
            <i class="fa fa-paste"></i>
          </el-icon>
        </el-form-item>
        <el-form-item label="Items (Full Path)">
          <el-tag type="primary">{{ result.extract_rules_css.items_full }}</el-tag>
          <el-icon style="margin-left:5px;cursor:pointer;" @click="() => onCopy(result.extract_rules_css.items_full)">
            <i class="fa fa-paste"></i>
          </el-icon>
        </el-form-item>
      </el-form>
    </el-tab-pane>

    <el-tab-pane label="Data" name="data">
      <el-table v-if="result" :data="result.extract_rules_css.data" :cell-style="{padding: '5px 10px'}" border>
        <el-table-column v-for="column in columns" :key="column.key" :prop="column.key" :label="column.label"/>
      </el-table>
    </el-tab-pane>
  </el-tabs>
</el-dialog>
`
};
