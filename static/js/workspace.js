
document.addEventListener('keydown', function (e) {
    if (e.key === "ArrowLeft") window.location.href = "{{ url_for('workspace', current_token=prev_token) }}";
    if (e.key === "ArrowRight") window.location.href = "{{ url_for('workspace', current_token=next_token) }}";
    if (e.key === "1") document.querySelector('button[value="1"]').click();
    if (e.key === "2") document.querySelector('button[value="2"]').click();
});