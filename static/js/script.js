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

document.addEventListener('DOMContentLoaded', function() {
    const algorithmSelect = document.getElementById('ml_algorithm');
    const targetColumnSelect = document.getElementById('target_column');
    const targetColumnFormGroup = targetColumnSelect ? targetColumnSelect.closest('.mb-3') : null;

    function toggleTargetColumn() {
        const selectedAlgorithm = algorithmSelect.value;
        // 无监督学习算法列表
        const unsupervisedAlgorithms = ['kmeans', 'dbscan', 'pca'];

        if (targetColumnSelect && targetColumnFormGroup) {
            if (unsupervisedAlgorithms.includes(selectedAlgorithm)) {
                // 无监督学习: 禁用目标特征选择并添加视觉反馈
                targetColumnSelect.disabled = true;
                targetColumnSelect.value = '';
                targetColumnFormGroup.classList.add('text-muted');
                targetColumnFormGroup.querySelector('.form-text').textContent = '无监督学习不需要目标变量';
            } else {
                // 监督学习: 启用目标特征选择
                targetColumnSelect.disabled = false;
                targetColumnFormGroup.classList.remove('text-muted');
                targetColumnFormGroup.querySelector('.form-text').textContent = '监督学习需选择目标变量';
            }
        }
    }

    // 初始化
    if (algorithmSelect) {
        toggleTargetColumn();
        algorithmSelect.addEventListener('change', toggleTargetColumn);
    }
});

/**
 * 当用户选择目标特征时，自动从特征选择列表中排除该特征
 */
document.addEventListener('DOMContentLoaded', function() {
    const targetColumnSelect = document.getElementById('target_column');
    const featureCheckboxes = document.querySelectorAll('input[name="features"]');

    targetColumnSelect.addEventListener('change', function() {
        const targetColumn = this.value;

        // 遍历所有特征复选框
        featureCheckboxes.forEach(checkbox => {
            if (checkbox.value === targetColumn) {
                // 如果是目标特征，取消选中并禁用
                checkbox.checked = false;
                checkbox.disabled = true;
            } else {
                // 其他特征恢复可选状态
                checkbox.disabled = false;
            }
        });
    });

    // 页面加载时初始化
    if (targetColumnSelect.value) {
        featureCheckboxes.forEach(checkbox => {
            if (checkbox.value === targetColumnSelect.value) {
                checkbox.checked = false;
                checkbox.disabled = true;
            }
        });
    }
});

document.addEventListener('DOMContentLoaded', function() {
    const algorithmSelect = document.getElementById('ml_algorithm');
    const targetColumnSelect = document.getElementById('target_column');
    const targetColumnFormGroup = targetColumnSelect ? targetColumnSelect.closest('.mb-3') : null;
    const numericTargetGroup = document.getElementById('numeric_target_group');
    const categoricalTargetGroup = document.getElementById('categorical_target_group');

    function toggleTargetColumn() {
        const selectedAlgorithm = algorithmSelect.value;
        // 无监督学习算法列表
        const unsupervisedAlgorithms = ['kmeans', 'dbscan', 'pca'];
        // 回归算法列表 (只需要数值型目标)
        const regressionAlgorithms = ['linear_regression', 'random_forest_regression'];
        // 分类算法列表 (只接受分类型目标)
        const classificationAlgorithms = ['random_forest_classification'];

        if (targetColumnSelect && targetColumnFormGroup) {
            if (unsupervisedAlgorithms.includes(selectedAlgorithm)) {
                // 无监督学习: 禁用目标特征选择
                targetColumnSelect.disabled = true;
                targetColumnSelect.value = '';
                targetColumnFormGroup.classList.add('text-muted');
                document.getElementById('target_column_help').textContent = '无监督学习不需要目标变量';

                // 启用所有特征复选框
                document.querySelectorAll('input[name="features"]').forEach(checkbox => {
                    checkbox.disabled = false;
                });
            } else {
                // 监督学习: 启用目标特征选择
                targetColumnSelect.disabled = false;
                targetColumnFormGroup.classList.remove('text-muted');

                // 根据算法类型显示相应的目标特征选项
                if (regressionAlgorithms.includes(selectedAlgorithm)) {
                    // 回归算法: 只显示数值型目标特征
                    numericTargetGroup.style.display = '';
                    categoricalTargetGroup.style.display = 'none';
                    document.getElementById('target_column_help').textContent = '回归算法需要选择数值型目标变量';

                    // 如果当前选择的不是数值型，清除选择
                    const selectedOption = targetColumnSelect.options[targetColumnSelect.selectedIndex];
                    if (selectedOption && selectedOption.getAttribute('data-type') !== 'numeric') {
                        targetColumnSelect.value = '';
                    }
                } else if (classificationAlgorithms.includes(selectedAlgorithm)) {
                    // 分类算法: 只显示分类型目标特征
                    numericTargetGroup.style.display = 'none';
                    categoricalTargetGroup.style.display = '';
                    document.getElementById('target_column_help').textContent = '分类算法需要选择分类型目标变量';

                    // 如果当前选择的不是分类型，清除选择
                    const selectedOption = targetColumnSelect.options[targetColumnSelect.selectedIndex];
                    if (selectedOption && selectedOption.getAttribute('data-type') !== 'categorical') {
                        targetColumnSelect.value = '';
                    }
                }

                // 如果已选择目标特征，更新特征选择框
                if (targetColumnSelect.value) {
                    updateFeatureCheckboxes(targetColumnSelect.value);
                }
            }
        }
    }

    function updateFeatureCheckboxes(targetColumn) {
        // 遍历所有特征复选框
        document.querySelectorAll('input[name="features"]').forEach(checkbox => {
            if (checkbox.value === targetColumn) {
                // 如果是目标特征，取消选中并禁用
                checkbox.checked = false;
                checkbox.disabled = true;
            } else {
                // 其他特征恢复可选状态
                checkbox.disabled = false;
            }
        });
    }

    // 初始化
    if (algorithmSelect) {
        toggleTargetColumn();
        algorithmSelect.addEventListener('change', toggleTargetColumn);
    }

    // 当目标特征改变时更新特征复选框
    if (targetColumnSelect) {
        targetColumnSelect.addEventListener('change', function() {
            updateFeatureCheckboxes(this.value);
        });

        // 页面加载时初始化
        if (targetColumnSelect.value) {
            updateFeatureCheckboxes(targetColumnSelect.value);
        }
    }
});