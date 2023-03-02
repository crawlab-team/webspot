import PlainListDialog from './plain-list-dialog.js';
import PaginationDialog from './pagination-dialog.js';

const {ref, computed} = Vue;
const {useStore} = Vuex;

export default {
  name: 'NavSidebar',
  components: {
    PlainListDialog,
    PaginationDialog,
  },
  setup() {
    const store = useStore();

    const activeRequestResults = computed(() => store.getters['activeRequestResults']);

    const isCollapsed = ref(false);
    const onToggle = () => {
      isCollapsed.value = !isCollapsed.value;
    };

    const onClickNode = (result) => {
      if (result.children) return;
      activeResult.value = result;
      dialogVisible.value = true;
    };

    const dialogVisible = ref(false);
    const onDialogClose = () => {
      dialogVisible.value = false;
    };

    const activeResult = ref({});

    const resultsTree = computed(() => {
      const res = Object.keys(activeRequestResults.value).map((key) => {
        const value = activeRequestResults.value[key];
        if (Array.isArray(value)) {
          const label = key;
          const children = value.map((item) => {
            return {
              label: item.name,
              ...item,
            };
          });
          return {
            label,
            children,
          };
        } else {
          return {
            label: key,
            ...value,
          };
        }
      });
      return res;
    });

    const getIcon = (data) => {
      if (data.children) {
        switch (data.label) {
          case 'pagination':
            return 'fa fa-compass';
          case 'plain_list':
            return 'fa fa-list';
        }
      } else {
        return 'fa fa-circle-o';
      }
    };

    return {
      activeRequestResults,
      isCollapsed,
      onToggle,
      onClickNode,
      dialogVisible,
      onDialogClose,
      activeResult,
      resultsTree,
      getIcon,
    };
  },
  template: `<div class="nav-sidebar" :style="{flexBasis: isCollapsed ? 'auto' : '240px'}">
  <h2 style="padding: 0 12px; height: 56px; margin: 0; display: flex; align-items: center">Detected Results</h2>
  <el-tree :data="resultsTree" :props="{class:'item-node'}" default-expand-all @node-click="onClickNode">
    <template v-slot="{node, data}">
      <div
       style="height: 100%; display: flex; align-items: center"
        :style="{fontSize: data.children ? '16px' : '14px', fontWeight: data.children ? 'bolder' : 'normal'}"
      >
        <el-icon size="16px">
          <i :class="getIcon(data)"></i>
        </el-icon>
        <span style="margin-left: 8px">
          {{ node.label }}
        </span>
        <span v-if="data.children" style="margin-left: 3px">({{ data.children.length }})</span>
        <el-tag v-if="data.score !== undefined" type="primary" style="margin-left: 10px;">
          <span class="score">{{ data.score.toFixed(2) }}</span>
        </el-tag>
      </div>
    </template>
  </el-tree>

  <plain-list-dialog
    v-show="activeResult.detector === 'plain_list'"
    :visible="dialogVisible"
    :result="activeResult"
    @close="onDialogClose"
   />
  <pagination-dialog
    v-show="activeResult.detector === 'pagination'"
    :visible="dialogVisible"
    :result="activeResult"
    @close="onDialogClose"
  />
</div>
`
};
