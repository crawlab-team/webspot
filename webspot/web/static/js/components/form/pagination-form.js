import BaseForm, {useBaseForm} from './base-form.js';

export default {
  name: 'PaginationForm',
  components: {
    BaseForm,
  },
  setup() {
    return {
      ...useBaseForm(),
    };
  },
  template: `
<base-form>
  <el-tab-pane label="Overview" name="overview">
    <el-form v-if="result" label-width="180px">
      <el-form-item label="Score">
        <el-tooltip content="Score (Overall)">
          <el-tag type="primary" style="margin-right: 5px">
            <i class="fa fa-star"></i>
            {{ result.score.toFixed(2) }}
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
</base-form>
`
};
