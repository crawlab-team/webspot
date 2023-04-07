window.addEventListener('message', (event) => {
  console.debug(event.data);
}, false);

document.querySelectorAll('*').forEach(el => {
  el.addEventListener('mouseover', (event) => {
    event.target.setAttribute('highlighted', 'true');
    event.stopPropagation();
  });

  el.addEventListener('mouseout', (event) => {
    event.target.setAttribute('highlighted', 'false');
    event.stopPropagation();
  });

  el.addEventListener('click', (event) => {
    event.stopPropagation();
    const el = event.target;
    const nodeId = el.getAttribute('node-id');
    window.parent.postMessage(nodeId);
  });
});
