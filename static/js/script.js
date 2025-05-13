document.addEventListener('DOMContentLoaded', () => {
  const dropZone = document.getElementById('drop-zone');
  const fileInput = document.getElementById('datafile');
  const fileNameDiv = document.getElementById('file-name');

  // 点击区域触发文件选择
  dropZone.addEventListener('click', () => fileInput.click());

  // 拖拽样式反馈
  dropZone.addEventListener('dragover', e => {
    e.preventDefault();
    dropZone.classList.add('dragover');
  });
  dropZone.addEventListener('dragleave', e => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
  });

  // 处理文件放下
  dropZone.addEventListener('drop', e => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    const files = e.dataTransfer.files;
    if (files.length) {
      fileInput.files = files;
      updateFileName();
    }
  });

  // 选择文件后显示文件名
  fileInput.addEventListener('change', updateFileName);

  function updateFileName() {
    if (fileInput.files.length > 0) {
      fileNameDiv.textContent = `已选择文件：${fileInput.files[0].name}`;
    } else {
      fileNameDiv.textContent = '';
    }
  }
});