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
 * 机器学习分析页面特征选择逻辑
 * 根据所选算法类型控制特征选择项的可用性
 */
function initializeMlAnalysisFeatureSelection() {
    // 检查是否在分析页面
    const algorithmSelect = document.getElementById('ml_algorithm');
    if (!algorithmSelect) return;

    // 获取算法选择下拉框和特征选择区域
    const targetSelect = document.getElementById('target_column');
    const featureCheckboxes = document.querySelectorAll('input[name="features"]');

    // 获取目标特征区域
    const targetFeatureDiv = document.querySelector('select#target_column').closest('.col-md-4');

    // 获取数值型列数据
    // 从后端直接接收数值型列列表
    const numericColumnsData = document.getElementById('numeric_columns_data');
    let numericColumns = [];
    if (numericColumnsData) {
        try {
            numericColumns = JSON.parse(numericColumnsData.textContent);
        } catch (e) {
            console.error('无法解析数值型列数据:', e);
        }
    }

    // 定义需要显示/隐藏参数区域的函数
    function toggleParamsVisibility() {
        // 隐藏所有参数区域
        document.querySelectorAll('.algorithm-params').forEach(div => {
            div.style.display = 'none';
        });

        // 获取选择的算法
        const selectedAlgorithm = algorithmSelect.value;

        // 显示对应的参数区域
        if (selectedAlgorithm) {
            const paramsDiv = document.getElementById(selectedAlgorithm + '_params');
            if (paramsDiv) {
                paramsDiv.style.display = 'block';
            }
        }

        // 处理监督学习和非监督学习的区别
        if (['linear_regression', 'random_forest_regression', 'random_forest_classification'].includes(selectedAlgorithm)) {
            targetFeatureDiv.style.display = 'block';
        } else {
            targetFeatureDiv.style.display = 'none';
            targetSelect.value = '';
        }

        // 处理非数值型特征的禁用逻辑
        const numericAlgorithms = ['linear_regression', 'random_forest_regression', 'kmeans', 'dbscan', 'pca'];

        if (numericAlgorithms.includes(selectedAlgorithm)) {
            featureCheckboxes.forEach(checkbox => {
                // 检查是否为数值型列
                const isNumeric = numericColumns.includes(checkbox.value);
                checkbox.disabled = !isNumeric;
                if (!isNumeric) checkbox.checked = false;
            });
        } else {
            // 分类算法可以使用所有列
            featureCheckboxes.forEach(checkbox => {
                checkbox.disabled = false;
            });
        }
    }

    // 当算法选择变化时
    algorithmSelect.addEventListener('change', toggleParamsVisibility);

    // 目标特征变化时，更新特征选择区
    targetSelect.addEventListener('change', function() {
        const targetValue = this.value;
        featureCheckboxes.forEach(checkbox => {
            // 如果是目标特征，则禁用该特征
            if (checkbox.value === targetValue) {
                checkbox.disabled = true;
                checkbox.checked = false;
            } else if (!algorithmSelect.value || algorithmSelect.value === 'random_forest_classification') {
                // 如果是分类算法或未选择算法，所有非目标特征都可选
                checkbox.disabled = false;
            } else {
                // 对于其他算法，只有数值型非目标特征可选
                const isNumeric = numericColumns.includes(checkbox.value);
                checkbox.disabled = !isNumeric;
            }
        });
    });

    // 初始运行一次来设置初始状态
    toggleParamsVisibility();
}

// 当DOM加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    initializeMlAnalysisFeatureSelection();
});