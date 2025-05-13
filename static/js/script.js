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

// 数据清洗页面功能
document.addEventListener('DOMContentLoaded', function() {
    // 控制填充值输入框的启用/禁用状态
    const dropMissingElem = document.getElementById('drop_missing');
    const fillMissingElem = document.getElementById('fill_missing');
    const fillValueElem = document.getElementById('fill_value');

    if (dropMissingElem && fillMissingElem && fillValueElem) {
        dropMissingElem.addEventListener('change', function() {
            fillValueElem.disabled = true;
        });

        fillMissingElem.addEventListener('change', function() {
            fillValueElem.disabled = false;
        });

        // 页面加载时初始化
        fillValueElem.disabled = !fillMissingElem.checked;
    }
});

document.addEventListener('DOMContentLoaded', function() {
    const algorithmSelect = document.getElementById('ml_algorithm');
    const paramDivs = document.querySelectorAll('.algorithm-params');
    function updateParams() {
        paramDivs.forEach(div => { div.style.display = 'none'; });
        const selectedAlgorithm = algorithmSelect.value;
        if (selectedAlgorithm) {
            const selectedParamDiv = document.getElementById(selectedAlgorithm + '_params');
            if (selectedParamDiv) selectedParamDiv.style.display = 'block';
        }
    }
    updateParams();
    algorithmSelect.addEventListener('change', updateParams);
});