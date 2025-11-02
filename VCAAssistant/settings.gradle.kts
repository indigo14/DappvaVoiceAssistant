pluginManagement {
    repositories {
        google {
            content {
                includeGroupByRegex("com\\.android.*")
                includeGroupByRegex("com\\.google.*")
                includeGroupByRegex("androidx.*")
            }
        }
        mavenCentral()
        gradlePluginPortal()
    }
}
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
        // Vosk is now available on Maven Central - no custom repository needed
        // maven { url = uri("https://alphacephei.com/maven/") }  // REMOVED - slow/unreliable
    }
}

rootProject.name = "VCA Assistant"
include(":app")
