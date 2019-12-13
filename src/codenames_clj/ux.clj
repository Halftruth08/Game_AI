(ns codenames-clj.ux
 (:require [clojure.java.io :as io]
   [clojure.string :as string]
   [seesaw.core :as ssw]
           )
  )

(defn popopen
  ""
  [title content]
  (let [fr (ssw/frame :title title, :content content, :on-close :exit)]
    (-> fr
        !pack
        !show))
   )