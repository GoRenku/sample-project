# Basilica — Renku sample project

This is a sample Renku movie project based on **Basilica**, a short film about the cannon founder Urban and the siege of Constantinople. The project includes its SQLite database, selected media, cast and location work, storyboards, and shot planning examples.

The screenplay is backed by [Final Draft XML](screenplay/edit/script.fdx). Edit that file in a compatible screenplay editor. In Renku Studio, review the detected external screenplay update before applying it. You can also explicitly import the edited file with `renku screenplay import-fdx --project sample-project --file screenplay/edit/script.fdx`.

The `visual-language/inspiration` collection is empty. Temporary generation output, superseded media, Trash, and unrelated research files were removed for this sample.

The Renku project database is tracked at `.renku/project.sqlite`; keep it when copying or publishing this folder.
