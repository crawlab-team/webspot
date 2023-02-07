const {ref, watch} = Vue;

export default {
  name: 'TopNavbar',
  props: {
    url: String,
  },
  setup(props, {emit}) {
    const internalUrl = ref(props.url);
    watch(() => props.url, () => internalUrl.value = props.url);
    const onUrlChange = (value) => {
      emit('change', value);
    };
    const onSubmit = () => {
      emit('submit');
    };
    return {
      internalUrl,
      onUrlChange,
      onSubmit,
    };
  },
  template: `<div class="top-navbar">
  <div class="logo-wrapper">
    <img src="/static/img/logo.svg">
  </div>
  <div class="url-wrapper" style="display: flex; flex: 0 0 360px;">
    <el-input id="url" type="text" placeholder="Please enter the URL" v-model="internalUrl" @change="onUrlChange" @keyup.enter="onSubmit"/>
    <el-button type="primary" @click="onSubmit" style="margin-left: 5px">Submit</el-button>
  </div>
</div>`
};
