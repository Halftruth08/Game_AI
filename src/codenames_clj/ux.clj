(ns codenames_clj.ux
 (:require [clojure.java.io :as io]
           [clojure.string :as string]
           [seesaw.core :as ssw]
           [seesaw.color :as color]
           )
  )



(defn popopen
  ""
  [title content]
  (let [fr (ssw/frame :title title, :content content, :on-close :exception)]
    (-> fr
        ssw/pack!
        ssw/show!))
   )
(defn blist
  ""
  [words]
  (map #(ssw/button :text %,
                    :font "ARIAL-BOLD-18",
                    ;:selected-text-color (color/color 255 255 0)
                    :listen [:action (fn [event] (ssw/alert %))]) words))

(def bgrid (ssw/grid-panel
             :border "Codenames"
             :columns 5
             :items (map #(ssw/button :text %,
                                      :font "ARIAL-BOLD-18",
                                      ;:selected-text-color (color/color 255 255 0)
                                      :listen [:action (fn [event] (ssw/alert %))]) (range 25))))
(def window1 (ssw/frame :title "Unchanged", :content bgrid))


(defn window
  ""
  [title content]
  (ssw/frame :title title, :content content))

(defn update_config
  [fr kw newcontent]
  (ssw/config! fr kw newcontent)
  (ssw/pack! fr))

(defn get_config
  ""
  [fr kw]
  (ssw/config fr kw))

(defn get_config_block
  ""
  [fr kw]
  (while (contains? #{"0000"} (ssw/config (ssw/config fr kw) :text))
    ;(println "waiting")
    ;(println (ssw/config (ssw/config fr kw) :text))
    (Thread/sleep 200)
    )
  (let [d (ssw/config fr kw)]
    (ssw/config! fr kw "0000")
    (ssw/config d :text))
  )


(defn show
  ""
  [fr]
  (-> fr
      ssw/pack!
      ssw/show!))

(defn lbl
  ""
  [stri]
  (ssw/label stri))

(defn button_or_field
  ""
  [word frout]
  (let [colors #{"red" "blue" "grey" "black"}]
    (if (contains? colors word)
      (ssw/label :text word,
                 :background (color/color word))
      (ssw/button :text word,
                  :font "ARIAL-BOLD-18",
                  ;:selected-text-color (color/color 255 255 0)
                  :listen [:action (fn [event] (ssw/config! frout :content word)
                                     ;(println word)
                                     )]))))

(defn buttons
  ""
  [words frout]
  (def bvec (map #(button_or_field % frout) words))
  (ssw/grid-panel
    :columns 5
    :items bvec))