import ListDialog from './list-dialog.js';

const {ref, computed, onBeforeMount} = Vue;

export default {
  name: 'NavSidebar',
  components: {
    ListDialog,
  },
  props: {
    results: String,
  },
  setup(props, {emit}) {
    const resultsArray = computed(() => {
      const resultsDecoded = window.atob(props.results);
      return JSON.parse(resultsDecoded);
    });

    const isCollapse = ref(false);
    const onToggle = () => {
      isCollapse.value = !isCollapse.value;
    };

    const onClickList = (result) => {
      activeResult.value = result;
      dialogVisible.value = true;
    };

    const dialogVisible = ref(false);
    const onDialogClose = () => {
      dialogVisible.value = false;
    };

    const activeResult = ref({});

    onBeforeMount(() => {
      console.debug(resultsArray.value);
    });

    return {
      resultsArray,
      isCollapse,
      onToggle,
      onClickList,
      dialogVisible,
      onDialogClose,
      activeResult,
    };
  },
  template: `<div class="nav-sidebar" :style="{flexBasis: isCollapse ? 'auto' : '240px'}">
  <el-menu :collapse="isCollapse" style="height: 100%">
    <el-menu-item v-for="(result, $index) in resultsArray" :key="$index" :index="$index" @click="() => onClickList(result)">
      <el-icon>
        <i class="fa fa-circle-o"></i>
      </el-icon>
      <span>{{ result.name }}</span>
      <el-tag type="primary" style="margin-left: 10px;">
        <span class="score">{{ result.stats.score.toFixed(2) }}</span>
        <span class="count"> ({{ result.nodes.items.length }})</span>
      </el-tag>
    </el-menu-item>
    <el-menu-item style="border-top: 1px solid #CCCCCC; position: absolute; bottom: 0; width: 100%" @click="onToggle">
      <el-icon>
        <DArrowRight v-if="isCollapse"/>
        <DArrowLeft v-else/>
      </el-icon>
      <span>{{ isCollapse ? 'Expand' : 'Collapse' }}</span>
    </el-menu-item>
  </el-menu>

  <list-dialog :visible="dialogVisible" :result="activeResult" @close="onDialogClose"/>
</div>
`
};
