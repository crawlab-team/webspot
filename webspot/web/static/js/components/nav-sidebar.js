const {ref, computed} = Vue;

export default {
  name: 'NavSidebar',
  props: {
    results: String,
  },
  setup(props) {
    const isCollapse = ref(false);
    const onToggle = () => {
      isCollapse.value = !isCollapse.value;
    };

    const resultsArray = computed(() => {
      const resultsDecoded = window.atob(props.results);
      return JSON.parse(resultsDecoded);
    });

    return {
      isCollapse,
      onToggle,
      resultsArray,
    };
  },
  template: `<div class="nav-sidebar" :style="{flexBasis: isCollapse ? 'auto' : '240px'}">
  <el-menu :collapse="isCollapse" style="height: 100%">
    <el-menu-item v-for="(result, $index) in resultsArray" :key="$index" :index="$index">
      <el-icon>
        <i class="fa fa-list"></i>
      </el-icon>
      <span>List {{ $index + 1 }}</span>
      <el-tag type="warning" style="margin-left: 10px;">{{ result.stats.score.toFixed(2) }}</el-tag>
    </el-menu-item>
    <el-menu-item style="border-top: 1px solid #CCCCCC; position: absolute; bottom: 0; width: 100%" @click="onToggle">
      <el-icon>
        <DArrowLeft v-if="isCollapse"/>
        <DArrowRight v-else/>
      </el-icon>
      <span>{{ isCollapse ? 'Expand' : 'Collapse' }}</span>
    </el-menu-item>
  </el-menu>
</div>
`
};
