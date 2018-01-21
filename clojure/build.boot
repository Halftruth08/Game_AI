(def project 'codenames-clj)
(def version "0.1.0-SNAPSHOT")

(set-env! :resource-paths #{"resources" "src"}
          :source-paths   #{"test"}
          :dependencies   '[[org.clojure/clojure "1.9.0" :scope "provided"]
                            [org.clojure/spec.alpha "0.1.143"]
                            [org.clojure/test.check "0.9.0"]
                            [org.clojure/core.async "0.4.474"]
                            [org.clojure/core.memoize "0.5.9"]
                            [org.clojure/tools.namespace "0.3.0-alpha4"]
                            [mount "0.1.11"]
                            [adzerk/boot-test "RELEASE" :scope "test"]])

(task-options!
 aot {:namespace   #{'codenames-clj.core}}
 pom {:project     project
      :version     version
      :description "FIXME: write description"
      :url         "http://example/FIXME"
      :scm         {:url "https://github.com/yourname/codenames-clj"}
      :license     {"Eclipse Public License"
                    "http://www.eclipse.org/legal/epl-v10.html"}}
 jar {:main        'codenames-clj.core
      :file        (str "codenames-clj-" version "-standalone.jar")})

(deftask build
  "Build the project locally as a JAR."
  [d dir PATH #{str} "the set of directories to write to (target)."]
  (let [dir (if (seq dir) dir #{"target"})]
    (comp (aot) (pom) (uber) (jar) (target :dir dir))))

(deftask run
  "Run the project."
  [a args ARG [str] "the arguments for the application."]
  (require '[codenames-clj.core :as app])
  (apply (resolve 'app/-main) args))

(require '[adzerk.boot-test :refer [test]])

(defn- generate-lein-project-file! []
  (require 'clojure.java.io)
  (let [pfile ((resolve 'clojure.java.io/file) "project.clj")
        ; Only works when pom options are set using task-options!
        {:keys [project version]} (:task-options (meta #'boot.task.built-in/pom))
        prop #(when-let [x (get-env %2)] [%1 x])
        head (list* 'defproject (or project 'boot-project) (or version "0.0.0-SNAPSHOT")
                    (concat
                      (prop :url :url)
                      (prop :license :license)
                      (prop :description :description)
                      [:dependencies (get-env :dependencies)
                       :repositories (get-env :repositories)
                       :source-paths (vec (concat (get-env :source-paths)
                                                  (get-env :resource-paths)))]))
        proj (pp-str head)]
    (spit pfile proj)))

(deftask lein-generate
         "Generate a leiningen `project.clj` file.
          This task generates a leiningen `project.clj` file based on the boot
          environment configuration, including project name and version (generated
          if not present), dependencies, and source paths. Additional keys may be added
          to the generated `project.clj` file by specifying a `:lein` key in the boot
          environment whose value is a map of keys-value pairs to add to `project.clj`."
         []
         (generate-lein-project-file!))

(deftask dev
         "Run when developing"
         []
         (lein-generate)
         (comp
           (watch)
           (repl :port 60000
                 :server true)
           #_(cljs :compiler-options {:output-wrapper true
                                    :pretty-print   false
                                    :compiler-stats true
                                    #_:closure-defines #_{"re_frame.trace.trace_enabled_QMARK_" true}
                                    :preloads       '[doublethedonation.dev #_day8.re-frame.trace.preload]}
                 :optimizations :none)))
