/**
 * Enhanced bulk actions with confirmation dialogs and select all functionality
 */
(function($) {
    'use strict';

    $(document).ready(function() {
        // Add select all checkbox in admin list
        var $actionSelect = $('#action');
        var $resultList = $('#result_list');
        
        if ($resultList.length && $actionSelect.length) {
            // Add select all checkbox
            var $thead = $resultList.find('thead');
            if ($thead.length) {
                var $firstRow = $thead.find('tr').first();
                var $firstCell = $firstRow.find('th').first();
                
                // Check if checkbox column exists
                if ($firstCell.find('input[type="checkbox"]').length === 0) {
                    $firstCell.prepend('<input type="checkbox" id="select-all" title="Select all">');
                } else {
                    $firstCell.find('input[type="checkbox"]').first().attr('id', 'select-all');
                }
            }
            
            // Select all functionality
            $(document).on('change', '#select-all', function() {
                var isChecked = $(this).is(':checked');
                $resultList.find('tbody input[type="checkbox"]').prop('checked', isChecked);
            });
            
            // Update select all when individual checkboxes change
            $resultList.find('tbody input[type="checkbox"]').on('change', function() {
                var total = $resultList.find('tbody input[type="checkbox"]').length;
                var checked = $resultList.find('tbody input[type="checkbox"]:checked').length;
                $('#select-all').prop('checked', total === checked && total > 0);
            });
        }
        
        // Confirmation dialogs for bulk actions
        var dangerousActions = {
            'archive_selected': {
                message: 'Are you sure you want to archive the selected items? Archived items will not be visible on the site.',
                title: 'Archive Items'
            },
            'draft_selected': {
                message: 'Are you sure you want to move the selected items to draft? They will not be visible on the site.',
                title: 'Move to Draft'
            },
            'delete_selected': {
                message: 'Are you sure you want to delete the selected items? This action cannot be undone and will also delete associated media files.',
                title: 'Delete Items'
            }
        };
        
        // Intercept form submission
        $('form#changelist-form').on('submit', function(e) {
            var $actionSelect = $('#action');
            var action = $actionSelect.val();
            var $checkedBoxes = $resultList.find('tbody input[type="checkbox"]:checked');
            
            if (action && $checkedBoxes.length > 0) {
                // Check if this is a dangerous action
                if (dangerousActions[action]) {
                    var confirmMsg = dangerousActions[action].message;
                    confirmMsg += '\n\nSelected items: ' + $checkedBoxes.length;
                    
                    if (!confirm(confirmMsg)) {
                        e.preventDefault();
                        return false;
                    }
                }
            }
        });
        
        // Show count of selected items
        function updateSelectedCount() {
            var count = $resultList.find('tbody input[type="checkbox"]:checked').length;
            if (count > 0) {
                var $submitButton = $('input[name="index"]').closest('form').find('button[type="submit"]');
                if ($submitButton.length) {
                    var originalText = $submitButton.data('original-text') || $submitButton.val();
                    $submitButton.data('original-text', originalText);
                    $submitButton.val(originalText + ' (' + count + ' selected)');
                }
            }
        }
        
        $resultList.find('tbody input[type="checkbox"]').on('change', updateSelectedCount);
        updateSelectedCount();
    });
})(django.jQuery);
