const {ref, computed, watch} = Vue;
const {ElMessage} = ElementPlus;

export default {
  name: 'PaginationDialog',
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
<el-dialog v-if="result.detector === 'pagination'" :title="result.name" v-model="dialogVisible" @close="onDialogClose" width="80%">
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
          <el-tooltip content="Sub-Score (URL Path Fragments)">
            <el-tag type="info" style="margin-right: 5px">
              <i class="fa fa-at"></i>
              {{ result.scores.url_path_fragments.toFixed(2) }}
            </el-tag>
          </el-tooltip>
          <el-tooltip content="Sub-Score (Feature Next)">
            <el-tag type="info" style="margin-right: 5px">
              <i class="fa fa-caret-right"></i>
              {{ result.scores.feature_next.toFixed(2) }}
            </el-tag>
          </el-tooltip>
          <el-tooltip content="Sub-Score (Text)">
            <el-tag type="info" style="margin-right: 5px">
              <i class="fa fa-file-text"></i>
              {{ result.scores.text.toFixed(2) }}
            </el-tag>
          </el-tooltip>
        </el-form-item>
        <el-form-item label="Selector Type">
          <el-radio-group v-model="selectorType">
            <el-radio label="css">CSS</el-radio>
            <el-radio label="xpath" disabled>XPath</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="Next">
          <el-tag type="primary">{{ result.selectors.next.selector }}</el-tag>
          <el-icon style="margin-left:5px;cursor:pointer;" @click="() => onCopy(result.selectors.next.selector)">
            <i class="fa fa-paste"></i>
          </el-icon>
        </el-form-item>
      </el-form>
    </el-tab-pane>
  </el-tabs>
</el-dialog>
`
};
