/**
 * FeretUI ERP Micro-interactions & Keyboard Shortcuts
 * Zero business logic in JS - HTMX trigger bindings only
 */

function initKanban() {
  if (typeof Sortable === 'undefined') return;
  document.querySelectorAll('.feretui-kanban-cards-container').forEach(function (container) {
    if (container._sortable) return;
    container._sortable = Sortable.create(container, {
      group: 'kanban-board',
      animation: 150,
      ghostClass: 'kanban-card-ghost',
      chosenClass: 'kanban-card-chosen',
      onEnd: function (evt) {
        var card = evt.item;
        var pk = card.getAttribute('data-pk');
        var newStage = evt.to.getAttribute('data-stage');
        var newIndex = evt.newIndex;
        var board = card.closest('.feretui-kanban-view');
        var moveUrl = board ? board.getAttribute('data-move-url') : null;
        if (moveUrl && pk && newStage) {
          if (typeof htmx !== 'undefined') {
            htmx.ajax('POST', moveUrl, {
              values: { pk: pk, stage: newStage, index: newIndex },
              swap: 'none'
            });
          }
        }
      }
    });
  });
}

document.addEventListener('DOMContentLoaded', function () {
  initKanban();

  if (typeof document.body !== 'undefined') {
    document.body.addEventListener('htmx:afterSwap', function () {
      initKanban();
    });
  }

  // Global Keyboard Shortcuts
  document.addEventListener('keydown', function (e) {
    const target = e.target;
    const tag = (target && target.tagName) ? target.tagName.toLowerCase() : '';
    const isInput = (tag === 'input' || tag === 'textarea' || tag === 'select');

    // Ctrl+S / Cmd+S : Save current form
    if ((e.ctrlKey || e.metaKey) && (e.key === 's' || e.key === 'S')) {
      e.preventDefault();
      const saveBtn = document.querySelector('[data-hotkey="save"], button[type="submit"].is-primary, button.is-primary[type="submit"]');
      if (saveBtn && !saveBtn.disabled) {
        saveBtn.click();
      }
      return;
    }

    // Escape : Cancel or close modal dialog
    if (e.key === 'Escape') {
      const dialog = document.querySelector('dialog[open]');
      if (dialog) {
        dialog.close();
        return;
      }
      const cancelBtn = document.querySelector('[data-hotkey="cancel"], a.is-ghost, button.is-ghost, button[type="reset"]');
      if (cancelBtn) {
        cancelBtn.click();
        return;
      }
    }

    // If typing in an input element, ignore non-modifier shortcuts
    if (isInput) return;

    // Alt+N : New / Create record
    if (e.altKey && (e.key === 'n' || e.key === 'N')) {
      e.preventDefault();
      const createBtn = document.querySelector('[data-hotkey="new"], button.button.is-primary[hx-get*="create"], a.button.is-primary[hx-get*="create"]');
      if (createBtn) {
        createBtn.click();
      }
      return;
    }

    // Alt+F : Focus search / filter
    if (e.altKey && (e.key === 'f' || e.key === 'F')) {
      e.preventDefault();
      const filterInput = document.querySelector('[data-hotkey="search"], input[name^="filter["], input[type="search"]');
      if (filterInput) {
        filterInput.focus();
        if (filterInput.select) filterInput.select();
      }
      return;
    }
  });
});
