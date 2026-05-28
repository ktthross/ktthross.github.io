---
# Feel free to add content and custom Front Matter to this file.
# To modify the layout, see https://jekyllrb.com/docs/themes/#overriding-theme-defaults

layout: home
---

<style>
main.page-content {
  background-image: url("/assets/main/IMG_1628.jpeg");
  background-size: cover;
  background-position: 42% 58%;
  background-repeat: no-repeat;
  min-height: calc(100vh - 56px);
  padding: 4rem 0;
}

main.page-content > .wrapper {
  background: rgba(255, 255, 255, 0.72);
  border-left: 4px solid rgba(30, 30, 30, 0.7);
  margin-left: max(2rem, calc((100vw - 1000px) / 2));
  margin-right: auto;
  max-width: 620px;
  padding: 1.75rem 2rem;
}

.home .post-list-heading,
.home .post-link {
  text-shadow: 0 1px 1px rgba(255, 255, 255, 0.85);
}

@media screen and (max-width: 700px) {
  main.page-content {
    background-position: 34% 58%;
    padding: 2rem 0;
  }

  main.page-content > .wrapper {
    margin-left: 1rem;
    margin-right: 1rem;
    padding: 1.25rem;
  }
}
</style>
