const {h} = Vue;
const {createStore} = Vuex;
const {ElNotification} = ElementPlus;

const defaultRequestForm = {
  method: 'request',
  no_async: false,
};

const store = createStore({
  state() {
    return {
      requests: [],
      activeRequestId: undefined,
      requestForm: undefined,
    };
  },
  getters: {
    isEmpty(state) {
      return state.requests.length === 0;
    },
    activeRequest(state) {
      return state.requests.find((request) => request._id === state.activeRequestId);
    },
    activeRequestStatus(state, getters) {
      return getters.activeRequest ? getters.activeRequest.status : '';
    },
    activeRequestResults(state, getters) {
      return getters.activeRequest ? getters.activeRequest.results : [];
    },
    activeRequestHtml(state, getters) {
      return getters.activeRequest ? getters.activeRequest.html : '';
    },
    activeRequestHtmlHighlighted(state, getters) {
      return getters.activeRequest ? getters.activeRequest.html_highlighted : '';
    },
    activeRequestFormattedError(state, getters) {
      if (!getters.activeRequest) return '';
      if (!getters.activeRequest.error) return '';
      return getters.activeRequest.error.split('\n').join('<br>');
    },
    requestForm(state) {
      if (state.requestForm) {
        return {...state.requestForm};
      }
      if (localStorage.getItem('requestForm')) {
        try {
          return JSON.parse(localStorage.getItem('requestForm'));
        } catch {
        }
      }
      localStorage.setItem('requestForm', JSON.stringify(defaultRequestForm));
      state.requestForm = {...defaultRequestForm};
      return {...defaultRequestForm};
    },
  },
  mutations: {
    setRequests(state, requests) {
      state.requests = requests;
    },
    setActiveRequestId(state, id) {
      state.activeRequestId = id;
    },
    setRequestForm(state, requestForm) {
      state.requestForm = {
        ...requestForm,
      };
      localStorage.setItem('requestForm', JSON.stringify({
        ...requestForm,
      }));
    },
    resetRequestForm(state) {
      localStorage.setItem('requestForm', JSON.stringify(defaultRequestForm));
      return {...defaultRequestForm};
    },
  },
  actions: {
    async getRequests({commit, state}) {
      const res = await axios.get(`/api/requests`);
      if (JSON.stringify(res.data) === JSON.stringify(state.requests)) {
        return;
      }
      commit('setRequests', res.data);

      // Set active request id if it's not set yet
      if (state.activeRequestId === undefined && res.data.length > 0) {
        commit('setActiveRequestId', res.data[0]._id);
      }
    },
    async postRequest({getters, commit, dispatch}, request) {
      const res = await axios.post(`/api/requests`, {
        ...getters.requestForm,
        ...request,
      });
      await ElNotification({
        title: 'Triggered request',
        message: h('span', [
          h('label', {}, ['URL: ']),
          h('a', {href: `${request.url}`, target: '_blank'}, [request.url]),
        ]),
        type: 'info',
      });
      await dispatch('getRequests');

      // Set result id as active
      commit('setActiveRequestId', res.data._id);
    },
  }
});

export default store;
