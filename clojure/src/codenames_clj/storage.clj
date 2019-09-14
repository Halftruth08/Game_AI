(ns codenames_clj.storage
  (:require [codenames_clj.model :as mdl]))
(require '[clojure.java.io :refer [file reader writer resource]])

(defn entry
  [word weight leaves]
  (clojure.string/join "\n" (list (clojure.string/join #"|" (list (str word) (str weight)))
                                  (clojure.string/join #"|" leaves))))

(defn restring
  [model]

  (clojure.string/join "\n"
                       (for [x model]
                         (let [xk (key x)
                               xv (seq (val x))]
                           (clojure.string/join "\n" (for [xkk (distinct (vals xv))]
                                                       (let [leaves (keys (filter #(= xkk (val %)) xv))]
                                                         (entry xk xkk leaves))))))))

(defn model-save
  "save to txt"
  [name model]
  (println (clojure.string/join ["Saving " name " with " (str (count model)) " entries"]))
  (let [m-name (clojure.string/join "/" ["resources" "models" name])
        out (restring model)]
    ;(println out)
    (spit m-name out)))
