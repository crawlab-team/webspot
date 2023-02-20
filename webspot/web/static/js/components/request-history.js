const {ref, computed, watch, onBeforeMount} = Vue;

export default {
  props: {
    requests: {
      type: Array,
      default() {
        return [];
      },
    },
  },
  setup(props) {
    const isCollapsed = ref(false);

    return {
      isCollapsed,
    };
  },
  template: `
<div class="request-history" :style="{flexBasis: isCollapsed ? 'auto' : '240px'}">
{{requests.length}}
</div>
`
};
